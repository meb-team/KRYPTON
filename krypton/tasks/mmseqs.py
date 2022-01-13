# -*- coding: utf-8

import krypton.utils as u

mmseqs_db_to_dl = ["UniRef100", "UniRef90", "UniRef50", "UniProtKB",
                   "UniProtKB/TrEMBL", "UniProtKB/Swiss-Prot", "NR", "NT",
                   "PDB", "PDB70", "Pfam-A.full", "Pfam-A.seed", "Pfam-B",
                   "eggNOG", "dbCAN2", "Resfinder", "Kalamari"]


def check_input_db_user(name):
    if name in mmseqs_db_to_dl:
        # A valild name for MMseqs-provided database
        return True
    elif u.is_file_exists(name) and u.check_seq_file_extension(name):
        # A valid FastA/Q[.gz]
        return True
    elif u.is_file_exists(name) and u.is_file_exists(name+'.dbtype') and \
            u.is_file_exists(name+'.index'):
        return True
    else:
        raise Exception(f"Krypton don't this MMseqs2 database: {name}.\n"
                        "There is probably an error in the name of the"
                        "database or the file ")


class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self, project=None, prot=None, module=None):
        self.module = 'easy-cluster' if not module else module
        self.threads = 8  # Ideally, this value would be provided by the user
        self.prot = prot
        self.subdir = self._get_subdir()
        self.output = project + "/" + self.subdir
        self.prefix = self.output + "/" + self.subdir
        self.tmp = project + "/tmp"
        u.create_dir(self.output)

    def _get_subdir(self):
        if not self.prot and (self.module == 'easy-cluster'):
            return "04_mmseqs"
        elif not self.prot and (self.module == 'createdb'):
            return "08_mmseq_search"
        elif self.prot:
            return "07_mmseqs"

    def command_cluster(self, seqs):
        # I know, this function looks useless, but I can't predict the future.
        # So let's keept it and see whether I can re-use it!
        command = f"mmseqs {self.module} {seqs} {self.prefix} {self.tmp}" +\
                  f" --threads {self.threads}"
        return command

    def mmseqs_createdb(self, seqs, db_prefix, logfile, step):
        """
        Add a way for a user-provided 'database'
            - fasta file (gzip or not)
            - preformated MMseqs2 database
            - database name? (need a download...)
        """
        command = f"mmseqs {self.module} {seqs} {self.output}/db/qryDB"
        with open(logfile, 'w') as log:
            u.run_command(command, log=log, step=step)
        return True

    def internal_db(self, seqs):
        """
        Setup the database for the proteins from KRYPTON, in 'self.output/db'
        """
        u.create_dir(self.output + "/db")
        self.mmseqs_createdb(seqs=seqs, db_prefix=f"{self.output}/db/qryDB",
                             logfile=self.output + "/mmseqs_qryDB_logs.log",
                             step="MMseqs - createdb - query")
        return True

    def ref_db(self, kind):
        """
        Reference database, one of these 3:
            - Provided by the user as a functionnal MMseqs2 db (kind = "ready")
            - Name of a dabatase ready to download by MMseqs2 (kind = "to_dl")
            - A f[aq][.gz] file (kind="to_format")
        """


if __name__ == '__main__':
    t = MMseqs2()
