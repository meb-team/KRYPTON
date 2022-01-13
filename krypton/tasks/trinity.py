# -*- coding: utf-8
import os
import glob

import krypton.utils as u

"""
Add something to test the presence of Trinity in the PATH, and the version
"""


class Trinity():

    def __init__(self, project=None):
        self.output = project + "/03_trinity"

    def format_command(self, r1, r2=None):
        """
        The Trinity parameter `--full_cleanup` change the behaviour of the tool
        WITHOUT: the result is {self.output}/Trinity.fa
        WITH: Trinity remove all temp files generated and output the results in
            {priject}/03_trinity.Trinity.fasta
        N.B., with this way, I have to trust Trinity for the dirrectory setup
        """
        command = f"{os.environ['TRINITY_HOME']}/Trinity --seqType fq " +\
                  "--full_cleanup --CPU 8 --max_memory 64G " +\
                  f"--output {self.output} "
        if r2:
            command += f"--left {r1} --right {r2}"
        else:
            command += f"--single {r1}"
        return command

    def clean(self):
        """ Clean everything after the run of Trinity"""

        # (re)Create the directory "03_trinity" and copy the results there
        u.create_dir(self.output)

        for file in glob.glob(f"{self.output}*.*"):
            file_base = os.path.basename(file)
            os.replace(file, f"{self.output}/{file_base}")

        # clean the names
        u.clean_deflines(infile=self.output + "/03_trinity.Trinity.fasta",
                         seq_prefix="seq")


if __name__ == '__main__':
    # ty = Trinity('damien/test_08')
    # ty.clean()
    toto = 1
