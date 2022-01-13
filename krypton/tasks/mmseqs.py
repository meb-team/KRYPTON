# -*- coding: utf-8

import krypton.utils as u


class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self, project=None, prot=None):
        self.module = 'easy-cluster'
        self.threads = 8  # Ideally, this value would be provided by the user
        self.prot = prot
        self.subdir = "04_mmseqs" if not self.prot else "07_mmseqs"
        self.output = project + "/" + self.subdir
        self.prefix = self.output + "/" + self.subdir
        self.tmp = self.output + "/tmp"
        u.create_dir(self.output)

    def command_cluster(self, seqs):
        # I know, this function looks useless, but I can't predict the future.
        # So let's keept it and see whether I can re-use it!
        command = f"mmseqs {self.module} {seqs} {self.prefix} {self.tmp}" +\
                  f" --threads {self.threads}"
        return command


if __name__ == '__main__':
    t = MMseqs2()
