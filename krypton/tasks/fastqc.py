# -*- coding: utf-8

import krypton.utils as u

"""
Add something to test the presence of FastQC in the PATH
"""


class FastQC():

    def __init__(self, raw=None, project=None):
        self.raw = raw
        self.output = f"{project}/00_fastqc_raw" if self.raw else \
                        f"{project}/02_fastqc_trimmed"
        u.create_dir(self.output)

    def format_command_fastqc(self, out, r1, r2=None):
        command = f"fastqc --outdir {self.output}"
        command = f"{command} {r1}" if not r2 else f"{command} {r1} {r2}"
        return command
