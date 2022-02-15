# -*- coding: utf-8

import time
import glob

import krypton.utils as u
import krypton.tasks.mmseqs as mmseqs
import krypton.tasks.fastqc as fastqc
import krypton.tasks.trinity as trinity
import krypton.tasks.antifam as antifam
import krypton.tasks.ko_annot as ko
import krypton.tasks.trimmomatic as trimmomatic
import krypton.tasks.transdecoder as transdecoder
import krypton.tasks.metapathexplorer as mpe


class Krypton:
    def __init__(self, args, abs_path):

        self.args = args
        A = lambda x: args.__dict__[x] if x in args.__dict__ else None
        self.abs_path = abs_path

        self.mode = A('mode')
        self.output = A('outdir').rstrip('/')
        # self.overwrite = A('overwrite')
        # ##### Reads
        self.paired = A('paired')
        self.r1 = A('r1')
        self.r2 = A('r2')
        # ##### Trimmomatic
        if self.mode == 'reads':
            self.trimmomatic = A('trimmomatic')
            self.trimmo_mod = "PE" if self.paired else "SE"
            trimmomatic.check_version(self.trimmomatic, mode=self.trimmo_mod)
        # #####
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
        # ##### Other parameters
        self.max_threads = 2 if not A('threads') else int(A('threads'))
        self.max_mem = '8G' if not A('mem') else A('mem') + 'G'
        """ Let's first make KRYPTON running on a regular computer. """
        # self.bucket_in = A('bucketin')
        # self.bucket_out = A('bucketout')
        # self.hpc2 = A('hpc2')

        # ## KEGG annotation setup
        self.ko_annot = A('ko_annot')
        self.ko_annot_file = A('ko_annot_file')

        if self.ko_annot:
            if not self.ko_annot_file:
                self.ko_annot_file = self.abs_path + "/ressources/KEGG_data"
            try:
                ko.ko_check_files(self.ko_annot_file)
            except Exception:
                print(f"Search in {self.ko_annot_file}")
                print("The files for K0 annotation are not present.\n"
                      "Please check the script\n\tdownload_K0famScan_data.py\n"
                      "KRYPTON will skip this step.\n")
                self.ko_annot = False

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

    def run_fastqc(self, r1, step=None, raw=False, r2=None):
        """ It assumes that FastQC is in the Path """
        f = fastqc.FastQC(r1=r1, r2=r2, raw=raw, project=self.output,
                          threads=self.max_threads, mem=self.max_mem)
        f.run_fastqc(step=step)
        return True

    def run_trimmomatic(self, step=None):
        t_params = "MINLEN:32 SLIDINGWINDOW:4:20 LEADING:5 TRAILING:5"
        t = trimmomatic.Trimmomatic(r1=self.r1, params=t_params, r2=self.r2,
                                    project=self.output, exec=self.trimmomatic,
                                    threads=self.max_threads)
        t.trimmomatic(step=step)
        return True

    def run_trinity(self, r1, r2=None, step=None):
        ty = trinity.Trinity(project=self.output, threads=self.max_threads,
                             mem=self.max_mem, r1=r1, r2=r2)
        ty.run_trinity(step=step)

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
        ms = mmseqs.MMseqs2(project=self.output, module='createdb',
                            threads=self.max_threads, mem=self.max_mem)

        # The CDS, from Krypton or the user
        ms.qry_db(seqs=cds_file)
        ms.ref_db(info_d=self.mmseq_sbj)
        ms.mmseqs_search(step="MMseqs - search")
        u.remove_dir(ms.tmp)

        # Converts the results DB into a tsv
        ms.mmseqsDB_to_tsv(step="MMseqs - convert - results in tsv")
        return True

    def run_prot_prediction(self, step=None, transcrits_clust=None):
        """
        Note about the parameters from the wiki: "the rate of false positive
        ORF predictions increases drastically with shorter minimum length
        """
        t = transdecoder.TransDecoder(transcripts=transcrits_clust,
                                      project=self.output,
                                      min_prot_len=self.min_prot_len)
        t.run_longorf(step=step)
        t.run_predict(step=step)
        t.clean()
        return True

    def remove_spurious_prot(self, step=None, prot=None):
        anti = antifam.Antifam(project=self.output, threads=self.max_threads,
                               proteins=prot, bin_path=self.abs_path)
        anti.run_antifam(step=step)
        anti.parse_antifam()
        return True

    def run_KO_annot(self, proteins, step=None):
        """ Protein annotation using KOFamScan and MetaPathExplorer"""
        k = ko.KO_annot(threads=self.max_threads, project=self.output,
                        ko_files=self.ko_annot_file,
                        proteins=proteins, bin_path=self.abs_path)
        k.run_kofamscan(format='detail-tsv', step=step)
        k.parse_results_for_MPE()
        k.parse_results_as_txt()
        return True

    def run_MetaPathExplorer(self, step=None):
        m = mpe.MPE(project=self.output, bin=self.abs_path)
        m.run_MPE(step=step)
        return True

    def run_krypton(self):
        print("\nKRYPTON is starting. All steps may take a lot of time. "
              "Please be patient...")
        time_global = [time.time()]

        if self.mode == "reads":
            # FastQC on the raw reads
            self.run_fastqc(r1=self.r1, step="FastQC - Raw reads", raw=True,
                            r2=self.r2)
            # Clean the reads
            self.run_trimmomatic(step="Trimmomatic")

            # FastQC on the cleaned reads
            clean_r1, clean_r2 = None, None
            if self.paired:
                clean_r1 = f"{self.output}/01_trimmomatic/r1.paired.fq"
                clean_r2 = f"{self.output}/01_trimmomatic/r2.paired.fq"
            else:
                clean_r1 = f"{self.output}/01_trimmomatic/r1.fq"

            self.run_fastqc(r1=clean_r1, step="FastQC - Trimmed reads",
                            r2=clean_r2)

            # Transcript assembly
            self.run_trinity(step=f"Trinity {'PE' if self.paired else 'SE'}"
                             " reads", r1=clean_r1, r2=clean_r2)

            # Save disk space: remove cleaned reads
            trimmomatic.clean(self.output)

        if self.mode != "cds":  # a.k.a reads or assembly
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
            glob.glob(self.output + '/06_*/*.pep.clean_defline.fa')[0]

        self.run_mmseqs_clust(seqs=cds_path, step="MMseqs cluster proteins",
                              prot=True)

        # Clean bad proteins
        prot_clusterised = glob.glob(f"{self.output}/" +
                                     "07_mmseqs/*_rep_seq.fasta")[0]
        self.remove_spurious_prot(step="AntiFam - removal of spurious seqs",
                                  prot=prot_clusterised)

        # Annotation
        good_proteins = glob.glob(f"{self.output}/" +
                                  "07_mmseqs_antifam/good_proteins.fa")[0]
        if self.mmseq_annot:
            self.run_mmseqs_search(cds_file=good_proteins)
        if self.ko_annot:
            self.run_KO_annot(proteins=good_proteins,
                              step="KOFamScan")

            """For the moment, MetaPAthExplorer is waiting a fix, about KEGG"""
            print("\nWarning: MPE is still buggy - ko/path/links must be",
                  "updated - so do not expect to have proper results!..")
            self.run_MetaPathExplorer(step="MetaPathExplorer: visualise" +
                                      "KEGG pathways")

        time_global.append(time.time())
        u.time_used(time_global, step="Krypton")
        return True
