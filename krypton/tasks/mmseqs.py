# -*- coding: utf-8

import krypton.utils as u

class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self):
        self.module = 'easy-cluster'
        self.threads = 8  # Ideally, this value would be provided by the user

    def command_cluster(self, transcripts, prefix, temp):
        # I know, this function looks useless, but I can't predict the future.
        # So let's keept it and see whether I can re-use it!
        command = f"mmseqs {self.module} {transcripts} {prefix} {temp}" +\
                  f" --threads {self.threads}"
        return command


if __name__ == '__main__':
    t = MMseqs2()
