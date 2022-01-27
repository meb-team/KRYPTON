# -*- coding: utf-8

import glob
import krypton.utils as u

"""
Add something to test the presence of Trimmomatic in the PATH
"""


class Trimmomatic():

    def __init__(self, raw=None, project=None, threads=None):
        self.max_threads = threads
        self.output = project + "/01_trimmomatic"
        u.create_dir(self.output)

    def format_command(self, bin, mod, r1, r2=None, params=None):
        command = f"java -jar {bin} {mod} -threads {self.max_threads} "
        if r2:
            command += f"{r1} {r2} {self.output}/r1.paired.fq " +\
                       f"{self.output}/r1.unpaired.fq {self.output}" +\
                       f"/r2.paired.fq {self.output}/r2.unpaired.fq "
        else:
            command += f"{r1} {self.output}/r1.fq "

        command += f"{'' if not params else params}"
        return command


def clean(project):
    for file in glob.glob(f"{project}/01_trimmomatic/*.fq"):
        u.remove_file(file)
    return True
