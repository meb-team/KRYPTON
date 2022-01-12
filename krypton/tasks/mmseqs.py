# -*- coding: utf-8

import krypton.utils as u


class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self):
        self.module = 'easy-cluster'
        self.threads = 8  # Ideally, this value would be provided by the user

    def command_cluster(self, seqs, prefix, temp):
        # I know, this function looks useless, but I can't predict the future.
        # So let's keept it and see whether I can re-use it!
        command = f"mmseqs {self.module} {seqs} {prefix} {temp}" +\
                  f" --threads {self.threads}"
        return command

    def setup_path_dir(self, out, clust_prot=None):
        sub_dir = "04_mmseqs"
        if clust_prot:
            sub_dir = "07_mmseqs"
        out_dir_mmseq = out + "/" + sub_dir
        out_prefix = out_dir_mmseq + "/" + sub_dir

        u.create_dir(out_dir_mmseq)

        return out_dir_mmseq, out_prefix


if __name__ == '__main__':
    t = MMseqs2()
