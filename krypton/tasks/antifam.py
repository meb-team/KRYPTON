# -*- coding: utf-8

import shutil
import krypton.utils as u


class Antifam():
    def __init__(self, threads=1, proteins=None, project=None, bin_path=None):
        self.max_threads = threads
        self.output = project + "/" + '07_mmseqs_antifam'
        self.input = proteins
        self.antifam = bin_path + "/ressources/AntiFam.hmm"

        u.create_dir(self.output)

    def run_antifam(self, step=None):
        self.hmmsearch_result = self.output + "/antifam_vs_proteins.tsv"
        command = f"hmmsearch --cpu {self.max_threads} --cut_ga " +\
                  f"--noali --tblout {self.hmmsearch_result} " +\
                  f"{self.antifam} {self.input}"

        print(command)

        with open(f"{self.output}/07_mmseqs_antifam_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def parse_antifam(self):
        self.good_prot = f"{self.output}/good_proteins.fa"
        self.bad_prot = f"{self.output}/bad_proteins.fa"

        list_bad_prot = list()
        with open(self.hmmsearch_result, 'r') as fi:
            lines = fi.readlines()
            for line in lines:
                if line.startswith("#"):
                    pass
                else:
                    list_bad_prot.append(line.split(' ')[0])

        if len(list_bad_prot) == 0:
            shutil.copy(self.input, self.good_prot)

        else:
            dict_p = dict()
            current_seq = ""
            current_name = ""
            with open(self.input, 'r') as fi:  # parse fasta
                if line[0] == ">":
                    if len(current_seq) != 0:
                        dict_p[current_name] = current_seq
                    current_name = line[1:].strip()
                    current_seq = ""
                else:
                    current_seq += line.rstrip()
            dict_p[current_name] = current_seq  # do not forget the last sequence

            # remove bad proteins from good ones
            with open(self.good_prot, 'w') as fo_good:
                with open(self.bad_prot, 'w') as fo_bad:
                    for prot, seq in dict_p.items():  # iterate over all prot
                        bool_bad_prot = 0
                        for elem in list_bad_prot:  # I cannot guarantee hmm
                            if elem in prot:
                                bool_bad_prot = 1
                                break
                        if bool_bad_prot:
                            print(prot, seq, sep="\n", file=fo_bad)
                        else:
                            print(prot, seq, sep="\n", file=fo_good)
        return True


if __name__ == '__main__':
    test = "damien/test_33"
    anti = Antifam(project=test, threads=8,
                   proteins=test+"/07_mmseqs/07_mmseqs_rep_seq.fasta",
                   bin_path="/home/dacourti/Documents/projects/MEB/KRYPTON")
    anti.run_antifam(step="run antifam")
    anti.parse_antifam()
