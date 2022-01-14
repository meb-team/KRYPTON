# -*- coding: utf-8
# import os
import time
import glob

import krypton.utils as u
import krypton.tasks.mmseqs as mmseqs
import krypton.tasks.fastqc as fastqc
import krypton.tasks.trinity as trinity
import krypton.tasks.trimmomatic as trimmomatic
import krypton.tasks.transdecoder as transdecoder

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
        self.mmseq_db = 'UniRef100' if not A('mmseq_db') else A('mmseq_db')
        self.mmseq_db_kind = None
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

        self.mmseq_db_kind = mmseqs.check_input_db(self.mmseq_db)

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
        f = fastqc.FastQC(raw=raw, project=self.output)

        with open(f.output + "/fastqc_logs.log", "w") as log:
            command = f.format_command_fastqc(f.output, r1, r2)
            u.run_command(command, log=log, step=step)
        return True

    def run_trimmomatic(self, step=None):
        t = trimmomatic.Trimmomatic(project=self.output)
        command = t.format_command(bin=self.trimmomatic, mod=self.trimmo_mod,
                                   r1=self.r1, r2=self.r2,
                                   params="MINLEN:32 SLIDINGWINDOW:10:20 " +
                                   "LEADING:5 TRAILING:5")
        with open(t.output + "/trimmomatic_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def run_trinity(self, step=None, r1=None, r2=None):
        ty = trinity.Trinity(project=self.output)
        command = ty.format_command(r1, r2)
        # With --full_cleanup, I have to let Trinity deal with its output dir
        with open(self.output + "/03_trinity_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        time.sleep(10)  # leave Trinity the time to clean its stuff
        ty.clean()
        return True

    def run_mmseqs_clust(self, step=None, seqs=None, prot=None):
        m = mmseqs.MMseqs2(project=self.output, prot=prot)
        command = m.command_cluster(seqs=seqs)
        with open(m.output + "/mmseqs_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        u.remove_dir(m.tmp)
        return True

    def run_mmseqs_search(self, cds_file):
        """
        This is a litteral transposition of Baptiste's work.
        I will tune it later.
        """
        ms = mmseqs.MMseqs2(project=self.output, module='createdb')

        # The CDS, from Krypton or the user
        ms.qry_db(seqs=cds_file)
        # The database reference db; 3 possible cases
        ms.ref_db(kind=self.mmseq_db_kind, infiles=self.mmseq_db)

        ms.mmseqs_search(step="MMseqs - search")

        # Converts the DB into a tsv
        ms.mmseqsDB_to_tsv(step="MMseqs - convert - results in tsv")

        u.remove_dir(ms.tmp)

    def run_prot_prediction(self, step=None, transcrits_clust=None):
        out_dir_long = self.output + "/05_transdecoder_longorfs"
        u.create_dir(out_dir_long)

        """
        Note about the parameters from the wiki: "the rate of false positive
        ORF predictions increases drastically with shorter minimum length
        """
        t = transdecoder.TransDecoder()
        command = t.format_longorf(transcrits_clust=transcrits_clust,
                                   outdir=out_dir_long, min_size=30)
        with open(out_dir_long + "/td_longorfs_logs.log", "w") as log:
            u.run_command(command, log=log, step=f"{step} - LongOrfs")

        """
        It is possible to run a PFAM annotation step for all the predicted CDS
        here. It could be better for TransDecoder.Predict
        """
        out_dir_pred = self.output + "/06_transdecoder_predict"
        u.create_dir(out_dir_pred)
        command_2 = t.format_predict(transcrits_clust=transcrits_clust,
                                     pred_input=out_dir_long)
        with open(out_dir_pred + "/td_predict_logs.log", "w") as log:
            u.run_command(command_2, log=log, step=f"{step} - Predict")

        t.clean(dest=out_dir_pred, transcripts=transcrits_clust,
                from_long=out_dir_long)
        # u.multi_to_single_line_fasta(glob.glob(f"{out_dir_pred}/*.transdecoder.pep")[0])
        return True

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
            transcripts_path = self.transcripts if self.transcripts else \
                    glob.glob(f"{self.output}/03_trinity/*clean_defline.fa")[0]

            self.run_mmseqs(step="MMseqs2 cluster transcripts",
                            seqs=transcripts_path)

            self.run_prot_prediction(step="TransDecoder",
                                     transcrits_clust=f"{self.output}/04_mmseqs/04_mmseqs_rep_seq.fasta")

        # Start from the cds provided by the user
        cds_path = self.cds if self.cds else \
            glob.glob(self.output + '/06_*/*.pep')[0]

        self.run_mmseqs_clust(seqs=cds_path, step="MMseqs cluster proteins",
                        prot=True)

        cds_clusterised = glob.glob(f'{self.output}/07_*/07_*_rep_seq.*')[0]
        self.run_mmseqs_search(cds_file=cds_clusterised)

        time_global.append(time.time())
        u.time_used(time_global, "Krypton")
