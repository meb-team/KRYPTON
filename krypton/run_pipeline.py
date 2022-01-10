# -*- coding: utf-8
# import os
import time

import krypton.utils as u


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
            if self.paired:
                self.run_fastqc(step="FastQC - Trimmed reads",
                                r1=f"{self.output}/01_trimmomatic/r1.paired.fq",
                                r2=f"{self.output}/01_trimmomatic/r2.paired.fq")
            else:
                self.run_fastqc(step="FastQC - Trimmed reads",
                                r1=f"{self.output}/01_trimmomatic/r1.fq")

        time_global.append(time.time())
        u.time_used(time_global, "Krypton")
