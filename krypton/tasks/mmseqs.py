# -*- coding: utf-8

import os
import krypton.utils as u

mmseqs_db_to_dl = ["UniRef100", "UniRef90", "UniRef50", "UniProtKB",
                   "UniProtKB/TrEMBL", "UniProtKB/Swiss-Prot", "NR", "NT",
                   "PDB", "PDB70", "Pfam-A.full", "Pfam-A.seed", "Pfam-B",
                   "eggNOG", "dbCAN2", "Resfinder", "Kalamari"]


def check_mmseq_db_param(db=None, db_path=None, out_json=None):
    if not db:
        if not db_path:
            print("\nYou did not provided a database to KRYPTON, so it "
                  "assumes you wish work with Swiss-Prot in your project "
                  "directory.")
        else:
            if u.is_file_exists(db_path) and \
             u.is_file_exists(db_path+'.dbtype') and \
             u.is_file_exists(db_path+'.index') and \
             u.is_file_exists(db_path+'_h'):
                return True
    elif db in mmseqs_db_to_dl:  # The name is valid
        if db_path:
            u.check_dir_exists(db_path, '--mmseq-db-path')
            print(f"The database will be downloaded and formated in {db_path}"
                  f"/{db}.\n")
        else:
            print("The database will be downloaded and formated in the "
                  "project directory.\n")
        return True
    elif u.check_seq_file_extension(db) and u.is_file_exists(db):  # Valid Fa
        if db_path:
            u.check_dir_exists(db_path, '--mmseq-db-path')
            print(f"The database will be formated in {db_path}/\n")
        else:
            print("The database will be formated in the project directory.\n")
        return True
    else:
        raise Exception('KRYPTON cannot handle the value passed to the param'
                        'meter "--mmseqs-db". Is there a typo in the name?')


def check_input_db_path(mmseq_db_path, db_kind):
    if db_kind == "db_ok":  # The user has provided a valid database
        return True
    elif db_kind == "db_to_dl":  # The user provided a db that has to be dl
        if not mmseq_db_path:  # The user does not want to store the db
            return True
        else:
            # dl and store the database where the user asked
            titi = 1
    # elif db_kind == "db_to_create":  # The user provided a Fa to setup the db
    #     if not mmseq_db_path:  # The user does not want to store the db
    #         toto = 1
    #     else:
    #         # setup and store the database where the user asked
    #         titi = 1
    # if not mmseq_db_path:
    #     toto = 1
    #     # Do something here


class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self, project=None, prot=None, module=None, threads=None,
                 mem=None):
        self.module = 'easy-cluster' if not module else module
        self.max_threads = threads
        self.max_mem = mem
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
        command = f"mmseqs {self.module} {seqs} {self.prefix} {self.tmp}" + \
                  f" --threads {self.max_threads} " + \
                  f"--split-memory-limit {self.max_mem}"
        return command

    def mmseqs_createdb(self, seqs, db_prefix, logfile, step):
        """
        Add a way for a user-provided 'database'
            - fasta file (gzip or not)
            - preformated MMseqs2 database
            - database name? (need a download...)
        """
        command = f"mmseqs {self.module} {seqs} {db_prefix}"
        with open(logfile, 'w') as log:
            u.run_command(command, log=log, step=step)
        return True

    def qry_db(self, seqs):
        """
        Setup the database for the proteins from KRYPTON, into 'self.output/db'
        """
        self.qry = f"{self.output}/db/qryDB"
        u.create_dir(self.output + "/db")
        self.mmseqs_createdb(seqs=seqs, db_prefix=self.qry,
                             logfile=self.output + "/mmseqs_qryDB_logs.log",
                             step="MMseqs - createdb - query")
        return True

    def mmseqs_dl_db(self, name, db_prefix, tmp, logfile, step):
        command = f"mmseqs databases {name} {db_prefix} {tmp}"
        with open(logfile, 'w') as log:
            u.run_command(command, log=log, step=step)
        return True

    def ref_db(self, kind, infiles):
        """
        Reference database, one of these 3:
            - Provided by the user as a functionnal MMseqs2 db (kind = "ready")
            - Name of a dabatase ready to download by MMseqs2 (kind = "to_dl")
            - A f[aq][.gz] file (kind="to_format")
        """
        self.sbj = ""
        if kind == "db_ok":
            self.sbj = infiles
            print("MMseqs database provided by the user is fine.")
        elif kind == "db_to_create":
            self.mmseqs_createdb(seqs=infiles,
                                 db_prefix=f"{self.output}/db/sbjDB",
                                 logfile=self.output + "/mmseqs_sbjDB_logs.log",
                                 step="MMseqs - createdb - subject - user seq")
            self.sbj = f"{self.output}/db/sbjDB"
        elif kind == "db_to_dl":
            self.mmseqs_dl_db(name=infiles, db_prefix=f"{self.output}/db/sbjDB",
                              tmp=self.tmp,
                              step="MMseqs - createdb - subject - download",
                              logfile=self.output + "/mmseqs_sbjDB_logs.log")
            self.sbj = f"{self.output}/db/sbjDB"
        return True

    def mmseqs_search(self, step, eval='1e-5', num_hit=100, sensitiv=7.5,
                      max_hit=1):
        """
        important parameters: -c --cov-mode --min-seq-id REVIEW THEM!!!
        """
        self.aln = f"{self.output}/db/resultDB"
        command = f"mmseqs search {self.qry} {self.sbj} {self.aln} " + \
                  f"{self.tmp} --threads {self.max_threads} " + \
                  f"--split-memory-limit {self.max_mem} -s {sensitiv} " + \
                  f"-e {eval} --max-seqs {num_hit} --max-accept {max_hit}"
        with open(f"{self.output}/mmseqs_search_logs.log", 'w') as log:
            u.run_command(command, log=log, step=step)
        return True

    def mmseqsDB_to_tsv(self, step):
        self.result = f"{self.output}/result.tsv"
        command = f"mmseqs convertalis {self.qry} {self.sbj} {self.aln} " + \
                  f"{self.result} --threads {self.max_threads} " + \
                  "--format-mode 2 -v 3"
        with open(f"{self.output}/mmseqs_convert_logs.log", 'w') as log:
            u.run_command(command, log=log, step=step)
        return True


if __name__ == '__main__':
    # t = MMseqs2()
    check_mmseq_db_param(db='Pfam-A.seed')
    check_mmseq_db_param(db='test.fa')
    check_mmseq_db_param(db='test.fa', db_path="/home/dacourti/databases")
    check_mmseq_db_param(db='Pfam-A.seeed')
