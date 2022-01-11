# -*- coding: utf-8
# import os
import time
import glob

import krypton.utils as u
import krypton.tasks.transdecoder as transdec


class Krypton:
    def __init__(self, args=None):
        self.args = args

        A = lambda x: args.__dict__[x] if x in args.__dict__ else None

        self.mode = A('mode')
        self.output = A('outdir').rstrip('/')
        # self.overwrite = A('overwrite')
        self.paired = A('paired')
        self.r1 = A('r1')
        self.r2 = A('r2')
        self.trimmomatic = A('trimmomatic')
        self.trimmo_mod = "PE" if self.paired else "SE"
        self.transcripts = A('transcripts')
        self.cds = A('cds')
        """ Let's first make KRYPTON running on a regular computer. """
        # self.bucket_in = A('bucketin')
        # self.bucket_out = A('bucketout')
        # self.hpc2 = A('hpc2')

        if self.mode == 'reads':
            if self.paired:
                if self.r1 is None or self.r2 is None:
                    raise Exception("Mode - READS:\n Please provides "
                                    "the paired-end reads via `--r1` **and**"
                                    " `--r2`, or use `--single-end`.")
                u.is_file_exists(self.r1)
                u.is_file_exists(self.r2)
            else:
                if self.r1 is None:
                    raise Exception("Mode - READS:\n Please provides at least "
                                    "one file for the reads.")
                u.is_file_exists(self.r1)

        if self.mode == "assembly":
            u.is_file_exists(self.transcripts)

        if self.mode == "cds":
            u.is_file_exists(self.cds)

        u.create_dir(self.output)

        """
        Just a reminder that I will have to
        add a step to check whether KRYPTON run on a regular
        server or on a HPC cluster.
        """

    def __repr__(self):
        return "Class instance Krypton\nCurrently KRYPTON runs with the " \
                + "following parameters:\n\tMode: {}\n".format(self.mode) \
                + "\tResult dir: {}/".format(self.output)

    def run_fastqc(self, step=None, raw=False, r1=None, r2=None):
        """ It assumes that FastQC is in the Path """
        out_dir_fastqc = f"{self.output}/00_fastqc_raw" if raw else \
                         f"{self.output}/02_fastqc_trimmed"
        u.create_dir(out_dir_fastqc)

        with open(out_dir_fastqc + "/fastqc_logs.log", "w") as log:
            command = u.format_command_fastqc(out_dir_fastqc, r1, r2)
            u.run_command(command, log=log, step=step)
        return True

    def run_trimmomatic(self, step=None):
        out_dir_trim = self.output + "/01_trimmomatic"
        u.create_dir(out_dir_trim)

        command = u.format_command_trimmomatic(out_dir_trim, self.trimmomatic,
                                               self.trimmo_mod, r1=self.r1,
                                               r2=self.r2, params="MINLEN:32" +
                                               " SLIDINGWINDOW:10:20" +
                                               " LEADING:5 TRAILING:5")
        with open(out_dir_trim + "/trimmomatic_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def run_trinity(self, step=None, r1=None, r2=None):
        out_dir_trinity = self.output + "/03_trinity"
        # u.create_dir(out_dir_trinity)

        command = u.format_command_trinity(out_dir_trinity, r1, r2)
        with open(f"{self.output}/03_trinity_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def run_mmseqs(self, module, step=None, transcripts=None):
        """
        all sequences for each cluster => <out>/<out>_all_seqs.fasta
        representative sequences  => <out>/<out>_rep_seq.fasta)
        identifiers for all cluster members => <out>/<out>_cluster.tsv
        """
        out_dir_mmseq = self.output + "/04_mmseqs"
        out_prefix = out_dir_mmseq + "/04_mmseqs"
        out_tmp = f"{self.output}/tmp"
        u.create_dir(out_dir_mmseq)
        command = u.format_command_mmseqs(transcripts, prefix=out_prefix,
                                          module=module,
                                          temp=out_tmp)

        with open(out_dir_mmseq + "/mmseqs_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)

        u.remove_dir(out_tmp)
        return True

    def run_prot_prediction(self, step=None, transcrits_clust=None):
        out_dir_pred = self.output + "/05_TransDecoder_ORF"
        u.create_dir(out_dir_pred)

        command = transdec.format_longorf(transcrits_clust=transcrits_clust,
                                          outdir=out_dir_pred + "/longorfs",
                                          min_size=30)
        with open(out_dir_pred + "/longorfs_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        u.remove_dir(out_dir_pred + "/longorfs.__checkpoints_longorfs",
                     other=True)
        transdec.remove_pipeliner(glob.glob("pipeliner.*.cmds"))
        return True

# if mode_pipeline == "assembly" or mode_pipeline == "reads":
#     os.system("TransDecoder.LongOrfs -m 30 -t {}".format(path_clust))
#     os.system("TransDecoder.Predict -t {}".format(path_clust))
#     os.system("python {}/modifi_format.py\
#             clusterRes_rep_seq.fasta.transdecoder.pep >\
#             clusterpep.fasta 2>&1".format(directory_KRYPTON))

    def run_krypton(self):
        print("\nKRYPTON is starting. All steps may take a lot of time. "
              "Please be patient...")
        time_global = [time.time()]

        if self.mode == "reads":
            self.run_fastqc(step="FastQC - Raw reads", raw=True, r1=self.r1,
                            r2=self.r2)
            self.run_trimmomatic(step="Trimmomatic")

            """
            Trimmomatic output the sentence
            'TrimmomaticPE: Completed successfully' in the logfile. It may
            be a good idea to implement a function that checks this and
            terminate the process in case of failure?
            """
            clean_r1 = f"{self.output}/01_trimmomatic/r1.paired.fq"
            clean_r2 = f"{self.output}/01_trimmomatic/r2.paired.fq"

            if self.paired:
                self.run_fastqc(step="FastQC - Trimmed reads",
                                r1=clean_r1, r2=clean_r2)
                self.run_trinity(step="Trinity", r1=clean_r1, r2=clean_r2)

            else:
                self.run_fastqc(step="FastQC - Trimmed reads", r1=clean_r1)

        if self.mode != "cds":  # a.k.a _reads_ or _assembly_
            transcripts_path = self.transcripts if self.transcripts \
                        else f"{self.output}/03_trinity.Trinity.fasta"

            self.run_mmseqs(module="easy-linclust",
                            step="MMseqs2 easy-linclust",
                            transcripts=transcripts_path)

            self.run_prot_prediction(step="TransDecoder",
                                     transcrits_clust=f"{self.output}/04_mmseqs/04_mmseqs_rep_seq.fasta")

        time_global.append(time.time())
        u.time_used(time_global, "Krypton")
