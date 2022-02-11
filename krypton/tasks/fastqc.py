# -*- coding: utf-8

import krypton.utils as u

"""
Add something to test the presence of FastQC in the PATH
"""


class FastQC():

    def __init__(self, r1, r2=None, raw=None, project=None, threads=None,
                 mem=None):
        """ Fastqc allocate 250MB per thread, so I have to check whether
        the number of threads required is in accordance with this rule
        """
        self.max_threads = threads
        while (self.max_threads * 0.25) > int(mem[:-1]):
            self.max_threads = self.max_threads // 2

        self.raw = raw
        self.output = f"{project}/00_fastqc_raw" if self.raw else \
                      f"{project}/02_fastqc_trimmed"
        self.r1 = r1
        self.r2 = r2

        u.create_dir(self.output)

    def run_fastqc(self, step=None):
        command = f"fastqc --outdir {self.output} --threads {self.max_threads}"
        if self.r2:
            command += f" {self.r1} {self.r2}"
        else:
            command += f" {self.r1}"

        with open(self.output + "/fastqc_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True
