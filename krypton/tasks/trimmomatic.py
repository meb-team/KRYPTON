# -*- coding: utf-8

import krypton.utils as u

"""
Add something to test the presence of Trimmomatic in the PATH
"""


class Trimmomatic():

    def __init__(self, raw=None, project=None):
        self.output = project + "/01_trimmomatic"
        u.create_dir(self.output)

    def format_command(self, bin, mod, r1, r2=None, params=None):
        command = f"java -jar {bin} {mod} "
        if r2:
            command += f"{r1} {r2} {self.output}/r1.paired.fq " +\
                       f"{self.output}/r1.unpaired.fq {self.output}" +\
                       f"/r2.paired.fq {self.output}/r2.unpaired.fq "
        else:
            command += f"{r1} {self.output}/r1.fq "

        command += f"{'' if not params else params}"
        return command
