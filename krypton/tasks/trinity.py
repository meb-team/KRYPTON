# -*- coding: utf-8
import os

import krypton.utils as u

"""
Add something to test the presence of Trinity in the PATH, and the version
"""


class Trinity():

    def __init__(self, project=None):
        self.output = project + "/03_trinity"
        u.create_dir(self.output)

    def format_command(self, r1, r2=None):
        """
        The Trinity parameter `--full_cleanup` change the behaviour of the tool
        WITHOUT: the result is {self.output}/Trinity.fa
        WITH: Trinity remove all temp files generated and output the results in
            {priject}/03_trinity.Trinity.fasta
        N.B., with this way, I have to trust Trinity for the dirrectory setup
        """
        command = f"{os.environ['TRINITY_HOME']}/Trinity --seqType fq " +\
                  f" --output {self.output} --CPU 8 --max_memory 64G --full_cleanup "
        if r2:
            command += f"--left {r1} --right {r2}"
        else:
            command += f"--single {r1}"
        return command
