# -*- coding: utf-8
import os
import glob
import time
import krypton.utils as u

"""
Add something to test the presence of Trinity in the PATH, and the version
"""


class Trinity():

    def __init__(self, r1, r2=None, project=None, threads=None, mem=None):
        self.max_threads = threads
        self.max_mem = mem
        self.r1 = r1
        self.r2 = r2
        self.project = project
        self.output = self.project + "/03_trinity"

    def run_trinity(self, step=None):
        """
        The Trinity parameter `--full_cleanup` change the behaviour of the tool
        WITHOUT: the result is {self.output}/Trinity.fa
        WITH: Trinity remove all temp files generated and output the results in
        {priject}/03_trinity.Trinity.fasta
        N.B., with this way, I have to trust Trinity for the dirrectory setup
        """
        command = ""
        if 'TRINITY_HOME' not in os.environ.keys():
            command += "Trinity "
        else:
            command += f"{os.environ['TRINITY_HOME']}/Trinity "
        command += "--seqType fq " + \
                   f"--full_cleanup --CPU {self.max_threads} " + \
                   f"--max_memory {self.max_mem} --output {self.output} "
        if self.r2:
            command += f"--left {self.r1} --right {self.r2}"
        else:
            command += f"--single {self.r1}"

        with open(self.project + "/03_trinity_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        # Leave Trinity the time to clean its stuff
        time.sleep(20)
        return True

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
        return True


if __name__ == '__main__':
    # ty = Trinity('damien/test_08')
    # ty.clean()
    toto = 1
