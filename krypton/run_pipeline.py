# -*- coding: utf-8
# import os
import time

import krypton.utils as u


class Krypton:
    def __init__(self, args=None):
        self.args = args

        A = lambda x: args.__dict__[x] if x in args.__dict__ else None

        self.mode = A('mode')
        self.output = A('outdir')
        # self.overwrite = A('overwrite')
        self.paired = A('paired')
        self.r1 = A('r1')
        self.r2 = A('r2')
        self.transcripts = A('transcripts')
        self.cds = A('cds')
        """ Let's first make KRYPTON running on a regular computer. """
        # self.bucket_in = A('bucketin')
        # self.bucket_out = A('bucketout')
        # self.hpc2 = A('hpc2')

        u.create_dir(self.output)

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
                    raise Exception("Mode - READS:\n Please provides the "
                                    "single-end reads only via `--r1`.")
                u.is_file_exists(self.r1)

        if self.mode == "assembly":
            u.is_file_exists(self.transcripts)

        if self.mode == "cds":
            u.is_file_exists(self.cds)

        """
        Just a reminder that I will have to
        add a step to check whether KRYPTON run on a regular
        server or on a HPC cluster.
        """

    def __repr__(self):
        return "Class instance Krypton\nCurrently KRYPTON runs with the " \
                + "following parameters:\n\tMode: {}\n".format(self.mode) \
                + "\tResult dir: {}/".format(self.output)

    def run_fastqc(self, step=None):
        """ It assumes that FastQC is in the Path """
        out_dir_fastqc = self.output + "/00_fastqc_raw"
        u.create_dir(out_dir_fastqc)
        with open(self.output + "/00_fastqc_raw/fastqc_logs.log", "w") as log:
            if self.paired:
                command = f"fastqc --outdir {out_dir_fastqc} " \
                          f"{self.r1} {self.r2}"
            else:
                command = f"fastqc --outdir {out_dir_fastqc} {self.r1}"
            u.run_command(command, log=log, step=step)
        return True

    def run_krypton(self):
        print("\nKRYPTON is starting. All steps may take a lot of time. "
              "Please be patient...")
        time_global = [time.time()]

        if self.mode == "reads":
            self.run_fastqc(step="FastQC - Raw reads")

        time_global.append(time.time())
        u.time_used(time_global, "Krypton")
