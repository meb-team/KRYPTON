# -*- coding: utf-8

import os
import krypton.utils as u

mmseqs_db_to_dl = ["UniRef100", "UniRef90", "UniRef50", "UniProtKB",
                   "UniProtKB/TrEMBL", "UniProtKB/Swiss-Prot", "NR", "NT",
                   "PDB", "PDB70", "Pfam-A.full", "Pfam-A.seed", "Pfam-B",
                   "eggNOG", "dbCAN2", "Resfinder", "Kalamari"]


def check_mmseq_db_param(db=None, db_path=None):
    info = {"db_ready_to_go": None, "db_user_input": None,
            "db_storage_path": None}

    if not db and not db_path:  # Nothing was provided, so SP within out
        info["db_user_input"] = "UniProtKB/Swiss-Prot"
        print(f'KRYPTON will work with {info["db_user_input"]} '
              'in the project directory.\n')

    elif not db and db_path:  # DB ready
        if u.is_file_exists(db_path) and \
         u.is_file_exists(db_path+'.dbtype') and \
         u.is_file_exists(db_path+'.index') and \
         u.is_file_exists(db_path+'_h'):  # Valid user-provided database
            info["db_ready_to_go"] = db_path
            print(f"KRYPTON will work with your database {db_path}\n")

    elif db in mmseqs_db_to_dl:  # The name is valid
        info["db_user_input"] = db
        if db_path:
            u.check_dir_exists(db_path, '--mmseq-db-path')
            info["db_storage_path"] = db_path.rstrip('/')
            print(f"KRYPTON will download the database {db} and format it "
                  f"in {db_path}.\n")
        else:
            print(f"KRYPTON will download the database {db} and format it "
                  "in the project directory.\n")

    elif u.check_seq_file_extension(db) and u.is_file_exists(db):  # Valid Fa
        info["db_user_input"] = db
        if db_path:
            u.check_dir_exists(db_path, '--mmseq-db-path')
            info["db_storage_path"] = db_path.rstrip('/')
            print(f"The database will be formated in {db_path}\n")
        else:
            print("The database will be formated in the project directory.\n")
    else:
        raise Exception('KRYPTON cannot handle the value passed to the param'
                        'meter "--mmseqs-db". Is there a typo in the name?')
    return info


class MMseqs2():
    """ Class that handle operations related to MMseqs2 """

    def __init__(self, project=None, prot=None, module=None, threads=None,
                 mem=None):
        self.module = module
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

    def mmseqs_cluster(self, seqs, step, cluster_mode=0, cov_mode=0):

        command = f"mmseqs {self.module} {seqs} {self.prefix} {self.tmp}" + \
                  f" --threads {self.max_threads} " + \
                  f"--split-memory-limit {self.max_mem} " +\
                  f"--cluster-mode {cluster_mode} --cov-mode {cov_mode}"
        with open(f"{self.output}/mmseqs_cluster_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

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

    def qry_db(self, seqs)c:
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

    def ref_db(self, info_d):
        logfile = self.output + "/mmseqs_sbjDB_logs.log"
        self.sbj = ""
        if info_d["db_ready_to_go"]:  # Database ready to go
            self.sbj = info_d["db_ready_to_go"]
            return True

        elif info_d["db_user_input"] in mmseqs_db_to_dl:  # DL and format DB
            if not info_d["db_storage_path"]:
                self.sbj = f"{self.output}/db/sbjDB"
                self.mmseqs_dl_db(name=info_d["db_user_input"],
                                  db_prefix=self.sbj, tmp=self.tmp,
                                  step="MMseqs - createdb - sbjct - download",
                                  logfile=logfile)
            else:
                self.sbj = f'{info_d["db_storage_path"]}/' +\
                           f'{info_d["db_user_input"].replace("/", "_")}DB'
                self.mmseqs_dl_db(name=info_d["db_user_input"],
                                  db_prefix=self.sbj,
                                  step="MMseqs - createdb - sbjct - download",
                                  tmp=self.tmp, logfile=logfile)

        else:  # User provides a sequence file
            if not info_d["db_storage_path"]:
                self.sbj = f"{self.output}/db/sbjDB"
                self.mmseqs_createdb(seqs=info_d["db_user_input"],
                                     db_prefix=self.sbj, logfile=logfile,
                                     step="MMseqs - createdb - sbjct" +
                                          " - User seq")
            else:
                self.sbj = f'{info_d["db_storage_path"]}/'
                self.sbj += os.path.basename(info_d["db_user_input"]) + 'DB'
                self.mmseqs_createdb(seqs=info_d["db_user_input"],
                                     db_prefix=self.sbj, logfile=logfile,
                                     step="MMseqs - createdb - sbjct -" +
                                     " User seq")
        return True

    def mmseqs_search(self, step, eval='1e-5', num_hit=100, sensitiv=7.5,
                      max_hit=1):
        """
        important parameters: -c --cov-mode --cluster-mode --min-seq-id REVIEW
        ==>Use --cluster-mode 2 or 3 + --cov-mode 1
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
