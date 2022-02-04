# -*- coding: utf-8
import os
import time
import glob

import krypton.utils as u
import krypton.tasks.mmseqs as mmseqs
import krypton.tasks.fastqc as fastqc
import krypton.tasks.trinity as trinity
import krypton.tasks.ko_annot as ko
import krypton.tasks.trimmomatic as trimmomatic
import krypton.tasks.transdecoder as transdecoder
import krypton.tasks.metapathexplorer as mpe


class Krypton:
    def __init__(self, args=None, abs_path=None):
        self.abs_path = os.path.dirname(abs_path) if abs_path else None

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
        self.min_prot_len = A('min_prot_len')

        # ## MMseqs2 annotation setup
        self.mmseq_annot = A('mmseq_annot')
        self.mmseq_db, self.mmseq_db_path, self.mmseq_sbj = None, None, None
        if self.mmseq_annot:
            self.mmseq_db = A('mmseq_db')
            self.mmseq_db_path = A('mmseq_db_path')
            self.mmseq_sbj = mmseqs.check_mmseq_db_param(
                                        db=self.mmseq_db,
                                        db_path=self.mmseq_db_path)
        # ## Other parameters
        self.max_threads = 2 if not A('threads') else int(A('threads'))
        self.max_mem = '8G' if not A('mem') else A('mem') + 'G'
        """ Let's first make KRYPTON running on a regular computer. """
        # self.bucket_in = A('bucketin')
        # self.bucket_out = A('bucketout')
        # self.hpc2 = A('hpc2')

        # ## KEGG annotation setup
        self.kegg_annot = A('kegg_annot')
        self.kegg_annot_file = A('kegg_annot_file')
        if self.kegg_annot:
            if not A('kegg_annot_file'):
                raise Exception("You asked for a KO annotation but you do "
                                "not provide the database to run on!\nPlease "
                                "pass something to `--kegg-ko-ref`.\n")
            if ko.ko_check_user_files(self.kegg_annot_file):
                self.kegg_annot_file = self.kegg_annot_file.rstrip('/')

        # ## Check the mode
        if self.mode == 'reads':
            if self.paired:
                if self.r1 is None or self.r2 is None:
                    raise Exception("Mode - READS:\n Please provides "
                                    "the paired-end reads via `--r1` **and**"
                                    " `--r2`, or use `--single-end`.")
                for file in [self.r1, self.r2]:
                    if not u.full_check_file(file):
                        raise Exception(f"The file {file} does not exist or"
                                        " has an unknown extention.")
            else:
                if self.r1 is None:
                    raise Exception("Mode - READS:\n Please provides at least "
                                    "one file for the reads.")
                if not u.full_check_file(self.r1):
                    raise Exception(f"The file {self.r1} does not exist or"
                                    " has an unknown extention.")

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
        f = fastqc.FastQC(raw=raw, project=self.output,
                          threads=self.max_threads, mem=self.max_mem)

        with open(f.output + "/fastqc_logs.log", "w") as log:
            command = f.format_command_fastqc(f.output, r1, r2)
            u.run_command(command, log=log, step=step)
        return True

    def run_trimmomatic(self, step=None):
        t = trimmomatic.Trimmomatic(project=self.output,
                                    threads=self.max_threads)
        command = t.format_command(bin=self.trimmomatic, mod=self.trimmo_mod,
                                   r1=self.r1, r2=self.r2,
                                   params="MINLEN:32 SLIDINGWINDOW:4:20 " +
                                   "LEADING:5 TRAILING:5")
        with open(t.output + "/trimmomatic_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def run_trinity(self, step=None, r1=None, r2=None):
        ty = trinity.Trinity(project=self.output, threads=self.max_threads,
                             mem=self.max_mem)
        command = ty.format_command(r1, r2)
        # With --full_cleanup, I have to let Trinity deal with its output dir
        with open(self.output + "/03_trinity_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        time.sleep(10)  # leave Trinity the time to clean its stuff
        ty.clean()
        return True

    def run_mmseqs_clust(self, step=None, seqs=None, prot=None):
        m = mmseqs.MMseqs2(project=self.output, prot=prot,
                           module='easy-cluster', threads=self.max_threads,
                           mem=self.max_mem)
        if not prot:
            m.mmseqs_cluster(seqs=seqs, step=step)
        else:
            m.mmseqs_cluster(seqs=seqs, step=step, cov_mode=1, cluster_mode=2)

        u.remove_dir(m.tmp)
        return True

    def run_mmseqs_search(self, cds_file):
        """
        This is a litteral transposition of Baptiste's work.
        I will tune it later.
        """
        ms = mmseqs.MMseqs2(project=self.output, module='createdb',
                            threads=self.max_threads, mem=self.max_mem)

        # The CDS, from Krypton or the user
        ms.qry_db(seqs=cds_file)
        ms.ref_db(info_d=self.mmseq_sbj)
        ms.mmseqs_search(step="MMseqs - search")
        u.remove_dir(ms.tmp)

        # Converts the DB into a tsv
        ms.mmseqsDB_to_tsv(step="MMseqs - convert - results in tsv")

    def run_prot_prediction(self, step=None, transcrits_clust=None):
        out_dir_long = self.output + "/05_transdecoder_longorfs"
        u.create_dir(out_dir_long)

        """
        Note about the parameters from the wiki: "the rate of false positive
        ORF predictions increases drastically with shorter minimum length
        """
        t = transdecoder.TransDecoder(min_prot_len=self.min_prot_len)
        command = t.format_longorf(transcrits_clust=transcrits_clust,
                                   outdir=out_dir_long)
        with open(out_dir_long + "/td_longorfs_logs.log", "w") as log:
            u.run_command(command, log=log, step=f"{step} - LongOrfs")

        """
        It is possible to run a PFAM annotation step for all the predicted CDS
        here.
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

    def run_KO_annot(self, proteins, step=None):
        """ Protein annotation using KOFamScan and MetaPathExplorer"""
        k = ko.KO_annot(threads=self.max_threads, project=self.output,
                        ko_files=self.kegg_annot_file,
                        proteins=proteins, bin_path=self.abs_path)
        k.run_kofamscan(format='detail-tsv', step=step)
        k.parse_results_for_MPE()

    def run_MetaPathExplorer(self, step=None):
        mpe.MPE(project=self.output, bin=self.abs_path)
        mpe.run_MPE(step=step)

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
                self.run_trinity(step="Trinity Paired-End reads",
                                 r1=clean_r1, r2=clean_r2)
            else:
                self.run_fastqc(step="FastQC - Trimmed reads", r1=clean_r1)
                self.run_trinity(step="Trinity Single-End reads", r1=clean_r1)

            trimmomatic.clean(self.output)

        if self.mode != "cds":  # a.k.a _reads_ or _assembly_
            transcripts_path = self.transcripts if self.transcripts else \
                    glob.glob(f"{self.output}/03_trinity/*clean_defline.fa")[0]

            self.run_mmseqs_clust(step="MMseqs2 cluster transcripts",
                                  seqs=transcripts_path)

            self.run_prot_prediction(step="TransDecoder",
                                     transcrits_clust=f"{self.output}/04_mmseqs/04_mmseqs_rep_seq.fasta")

        # Start from the cds provided by the user
        """ This step would require an extra check, in case of failure
        from TansDecoder-Predict"""
        cds_path = self.cds if self.cds else \
            glob.glob(self.output + '/06_*/*.pep')[0]

        self.run_mmseqs_clust(seqs=cds_path, step="MMseqs cluster proteins",
                              prot=True)

        # Annotation
        prot_clusterised = glob.glob(f'{self.output}/07_*/07_*_rep_seq.*')[0]
        if self.mmseq_annot:
            self.run_mmseqs_search(cds_file=prot_clusterised)
        if self.kegg_annot:
            self.run_KO_annot(proteins=prot_clusterised,
                              step="KOFamScan")

            """For the moment, MetaPAthExplorer is waiting a fix, about KEGG"""
            # self.run_MetaPathExplorer(step="MetaPathExplorer: visualise" +
            #                           "KEGG pathways")

        time_global.append(time.time())
        u.time_used(time_global, step="Krypton")
