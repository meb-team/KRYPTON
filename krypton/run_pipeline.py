# -*- coding: utf-8

import os
import time
import glob

from krypton import utils as u
from krypton.tasks import ko_annot as ko
from krypton.tasks import mmseqs, fastqc, trinity, antifam, trimmomatic, transdecoder
# import krypton.tasks.metapathexplorer as mpe  # Deprecated


class Krypton:
    """Main class that controls the pipeline"""
    def __init__(self, args):

        self.args = args
        A = lambda x: args.__dict__[x] if x in args.__dict__ else None
        self.abs_path = os.path.dirname(os.path.realpath(__file__))

        self.mode = A('mode')
        self.output = A('outdir').rstrip('/')
        self.bindpoint = A('bindpoint').rstrip('/') if A('bindpoint') else None
        # self.overwrite = A('overwrite')
        # ##### Reads
        self.paired = A('paired')
        self.r1 = A('r1')
        self.r2 = A('r2')

        # # ##### Trimmomatic
        # kept for consistency, DEPRECATED , only use the binary called
        # "trimmomatic"
        # if self.mode == 'reads':
        #     self.trimmomatic = A('trimmomatic')
        #     self.trimmo_mod = "PE" if self.paired else "SE"
        #     trimmomatic.check_version(self.trimmomatic, mode=self.trimmo_mod)
        # # #####

        self.transcripts = A('transcripts')
        self.no_transcript_cluster = A('no_transcript_cluster')
        self.cds = A('cds')
        self.no_cds_cluster = A("no_cds_cluster")
        self.min_prot_len = A('min_prot_len')

        # ## MMseqs2 annotation setup
        self.mmseq_annot = A('mmseq_annot')
        self.mmseq_db, self.mmseq_db_path, self.mmseq_sbj = None, None, {}
        if self.mmseq_annot:
            self.mmseq_db = A('mmseq_db')
            self.mmseq_db_path = A('mmseq_db_path')
            self.mmseq_sbj = mmseqs.check_mmseq_db_param(
                                        db=self.mmseq_db,
                                        db_path=self.mmseq_db_path)
        # ##### Other parameters
        self.max_threads = 2 if not A('threads') else int(A('threads'))
        self.max_mem = '16G' if not A('mem') else A('mem') + 'G'
        self.assembly_only = A('assembly_only')
        """ Let's first make KRYPTON running on a regular computer. """
        # self.bucket_in = A('bucketin')
        # self.bucket_out = A('bucketout')
        # self.hpc2 = A('hpc2')

        # ## KEGG annotation setup
        self.ko_annot = A('ko_annot')
        if self.ko_annot:
            try:
                ko.ko_check_files(self.ko_annot)
                print("\nFiles for the annotation via K0FamScan are correct!")
            except NotImplementedError:
                print(f"\nSearch in {self.ko_annot}")
                print("The files for K0 annotation are not present or not "
                      "valid.\nPlease check the script\n\t"
                      "KRYPTON_download_K0famScan_data.py\n"
                      "KRYPTON will skip this annotation step.\n"
                      "==> Kill the process if you want it.")

        # ## Check the mode
        if self.mode == 'reads':
            if self.paired:
                if self.r1 is None or self.r2 is None:
                    raise FileNotFoundError("Mode - READS:\n Please provides "
                                            "the paired-end reads via `--r1` "
                                            "**and** `--r2`, or use "
                                            "`--single-end`.")
                for file in [self.r1, self.r2]:
                    if not u.full_check_file(file):
                        raise FileExistsError(f"The file {file} does not exist"
                                              " or has an unknown extention.")
            else:
                if self.r1 is None:
                    raise FileNotFoundError("Mode - READS:\n Please provides at"
                                            " least one file for the reads.")
                if not u.full_check_file(self.r1):
                    raise FileExistsError(f"The file {self.r1} does not exist "
                                          "or has an unknown extention.")

        if self.mode == "assembly":
            u.is_file_exists(self.transcripts)
            if self.assembly_only:
                print("Why did you turned ON the '--assembly-only' ? let's "
                      "guess it is a copy/paste error. Krypton continues "
                      "anyway. Otherwise hit CTRL+C!")
                self.assembly_only = False

        if self.mode == "cds":
            u.is_file_exists(self.cds)
            if self.assembly_only:
                print("Why did you turned ON the '--assembly-only' ? let's "
                      "guess it is a copy/paste error. Krypton continues "
                      "anyway. Otherwise hit CTRL+C!")
                self.assembly_only = False

        u.create_dir(self.output)

        # Just a reminder that I will have to
        # add a step to check whether KRYPTON run on a regular
        # server or on a HPC cluster.

    def __repr__(self):
        return "Class instance Krypton\nCurrently KRYPTON runs with the " \
                + f"following parameters:\n\tMode: {self.mode}\n" \
                + f"\tResult dir: {self.output}/"

    def run_fastqc(self, r1, step=None, raw=False, r2=None):
        """ It assumes that FastQC is in the Path """
        f = fastqc.FastQC(r1=r1, r2=r2, raw=raw, project=self.output,
                          threads=self.max_threads, mem=self.max_mem)
        f.run_fastqc(step=step)
        return True

    def run_trimmomatic(self, step=None):
        """Run the tool Trimmomatic, parameters are set in the function
        Possible improvments: replace by "fastp"; leave the user the possibility
        to choose the parameters
        """
        t_params = "MINLEN:32 SLIDINGWINDOW:4:20 LEADING:5 TRAILING:5"
        t = trimmomatic.Trimmomatic(r1=self.r1, params=t_params, r2=self.r2,
                                    project=self.output,
                                    threads=self.max_threads)
        t.trimmomatic(step=step)
        return True

    def run_trinity(self, r1, r2=None, step=None):
        """Run the RNAseq transcripts assembly"""
        ty = trinity.Trinity(project=self.output, threads=self.max_threads,
                             mem=self.max_mem, r1=r1, r2=r2)
        ty.run_trinity(step=step)

        ty.clean()
        return True

    def run_mmseqs_clust(self, step=None, seqs=None, prot=None):
        """Clustering with MMseqs easy-cluster"""
        m = mmseqs.MMseqs2(project=self.output, prot=prot,
                           module='easy-cluster', threads=self.max_threads,
                           mem=self.max_mem)
        if not prot:
            m.mmseqs_cluster(seqs=seqs, step=step)
        else:
            m.mmseqs_cluster(seqs=seqs, step=step, cov_mode=1, cluster_mode=2)

        if not self.bindpoint:
            try:
                u.remove_dir(m.tmp)  # Do not remove if run from Singularity img
            except NotImplementedError:
                # temp dir is not removed, but do not stop the job
                pass
        return True

    def run_mmseqs_search(self, cds_file):
        """Search predicted proteins against a database to find relevant hits
        With MMseqs """
        ms = mmseqs.MMseqs2(project=self.output, module='createdb',
                            threads=self.max_threads, mem=self.max_mem)

        # The CDS, from Krypton or the user
        ms.qry_db(seqs=cds_file)
        ms.ref_db(info_d=self.mmseq_sbj)
        ms.mmseqs_search(step="MMseqs - search")

        if not self.bindpoint:
            try:
                u.remove_dir(ms.tmp)  # Do not remove if run from Singularity img
            except NotImplementedError:
                # temp dir is not removed, but do not stop the job
                pass

        # Converts the results DB into a tsv
        ms.mmseqs_db_to_tsv(step="MMseqs - convert - results in tsv")
        return True

    def run_prot_prediction(self, step=None, transcrits_clust=None):
        """
        Note about the parameters from the wiki: "the rate of false positive
        ORF predictions increases drastically with shorter minimum length
        """
        t = transdecoder.TransDecoder(transcripts=transcrits_clust,
                                      project=self.output,
                                      min_prot_len=self.min_prot_len,
                                      bindpoint=self.bindpoint)
        t.run_longorf(step=step)
        t.run_predict(step=step)
        t.clean()
        return True

    def remove_spurious_prot(self, step=None, prot=None):
        """Search Antifam profiles against the proteins to identify
        spurious prediction"""
        anti = antifam.Antifam(project=self.output, threads=self.max_threads,
                               proteins=prot, bin_path=self.abs_path)
        anti.run_antifam(step=step)
        anti.parse_antifam()
        return True

    def run_ko_annot(self, proteins, step=None):
        """ Protein annotation using KOFamScan"""
        k = ko.KoAnnot(threads=self.max_threads, project=self.output,
                        ko_files=self.ko_annot, proteins=proteins)

        if not self.bindpoint:
            k.run_kofamscan(outfmt='detail-tsv', step=step)
            # k.parse_results_for_MPE()
            # k.parse_results_as_txt()

        else:
            k.get_command(output=True, bindpoint=self.bindpoint,
                          outfmt='detail-tsv')
        return True

    # def run_MetaPathExplorer(self, step=None):  # DEPRECATED
    #     m = mpe.MPE(project=self.output, bin=self.abs_path)
    #     m.run_MPE(step=step)
    #     return True

    def run_krypton(self):
        """Function that controls the pipeline"""
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

            # Reduce transcript redundancy
            if not self.no_transcript_cluster:
                self.run_mmseqs_clust(step="MMseqs2 cluster transcripts",
                                      seqs=transcripts_path)
                transcrits_clust = f"{self.output}/04_mmseqs/" \
                                   "04_mmseqs_rep_seq.fasta"
            else:
                print("-- Skip clustering of Trinity transcripts --")
                transcrits_clust = transcripts_path

            # Stop here if the user wants only the assembly
            if self.assembly_only:
                try:
                    u.remove_dir(self.output + '/tmp')
                except NotImplementedError:
                    pass
                time_global.append(time.time())
                u.time_used(time_global, step="Krypton")
                return True

            # Predict the proteins
            self.run_prot_prediction(step="TransDecoder",
                                     transcrits_clust=transcrits_clust)

        # Start from the cds provided by the user
        # ## This step would require an extra check, in case of failure
        # ## from TansDecoder-Predict"""
        cds_path = self.cds if self.cds else \
            glob.glob(self.output + '/06_*/*.pep.clean_defline.fa')[0]

        # The clustering of proteins is wanted (default behaviour)
        if not self.no_cds_cluster:
            self.run_mmseqs_clust(seqs=cds_path,
                                  step="MMseqs cluster proteins", prot=True)
            prot_clusterised = glob.glob(f"{self.output}/" +
                                         "07_mmseqs/*_rep_seq.fasta")[0]
        else:
            prot_clusterised = cds_path

        # Clean bad proteins
        self.remove_spurious_prot(step="AntiFam - removal of spurious seqs",
                                  prot=prot_clusterised)

        # Annotation
        good_proteins = f"{self.output}/07_mmseqs_antifam/good_proteins.fa"
        if self.mmseq_annot:
            self.run_mmseqs_search(cds_file=good_proteins)
        if self.ko_annot:
            if not self.bindpoint:
                self.run_ko_annot(proteins=good_proteins,
                                  step="KOFamScan")

                # ## Deprecated code bellow
                # print("\nWarning: MPE is still buggy - ko/path/links must be",
                #       "updated - so do not expect to have proper results!..")
                # self.run_MetaPathExplorer(step="MetaPathExplorer: visualise" +
                #                           "KEGG pathways")
            else:
                self.run_ko_annot(proteins=good_proteins,
                                  step="Prepare script for KoFamScan")

        time_global.append(time.time())
        u.time_used(time_global, step="Krypton")
        return True
