# -*- coding: utf-8

import os
import glob
import shutil
import subprocess
from subprocess import CalledProcessError

import krypton.utils as u


class TransDecoder():

    def __init__(self, transcripts, project=None, min_prot_len=None,
                 bindpoint=None):
        self.required_version = "5.5.0"
        self._check_avail()
        self._check_version()
        self.min_prot_len = min_prot_len
        self.project = project
        self.transcripts = transcripts
        self.out_long = self.project + "/05_transdecoder_longorfs"
        self.out_pred = self.project + "/06_transdecoder_predict"
        self.bindpoint = bindpoint

        u.create_dir(self.out_long)
        u.create_dir(self.out_pred)

    def _check_avail(self):
        try:
            subprocess.run(["TransDecoder.LongOrfs", "--version"], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except (FileNotFoundError, CalledProcessError) as e:
            if e == 'FileNotFoundError':
                print("The excecutable for TransDecoder.LongOrfs is not ",
                      "present in your PATH")
            else:
                print("One of the parameter provided to TransDecoder.LongOrfs",
                      " is wrong.")
            return False
        return True

    def _check_version(self):
        version = subprocess.check_output(['TransDecoder.LongOrfs',
                                          '--version'], encoding='utf-8')
        version_found = version.rstrip().split(" ")[1]
        if version_found != self.required_version:
            raise Exception("Wrong TransDecoder version. EXPECTED " +
                            f"{self.required_version}, FOUND {version_found}.")
        return True

    def __repr__(self):
        return f"TransDecoder Object, tool version : {self.required_version}"

    def run_longorf(self, step=None):
        command = f"TransDecoder.LongOrfs --output_dir {self.out_long}"\
                  + f" -t {self.transcripts} -m {self.min_prot_len}"
        with open(self.out_long + "/td_longorfs_logs.log", "w") as log:
            u.run_command(command, log=log, step=f"{step} - LongOrfs")
        return True

    def run_predict(self, step=None, pfam=None, pfam_res=None):
        command_p = f"TransDecoder.Predict --output_dir {self.out_long}"\
                  + f" -t {self.transcripts}"
        if pfam:
            """
            It is possible to add run PFam annot on the proteins first, but we
            choosed to not doing it as we have several annotations steps after.
            """
            command_p += f" --retain_pfam_hits {pfam_res}"
        with open(self.out_pred + "/td_predict_logs.log", "w") as log:
            u.run_command(command_p, log=log, step=f"{step} - Predict")
        return True

    def clean(self):
        """
        Clean the mess that Transdecoder is producing
        Giving this issue
        (https://github.com/TransDecoder/TransDecoder/issues/108)
        I guess it would be better for me to move the result files myself, not
        waiting for a TransDecoder update.
        """
        # I have to hardcode those names. It is the only fix I found to run
        # KRYPTON within a Singularity container
        res_files = ["04_mmseqs_rep_seq.fasta.transdecoder.bed",
                     "04_mmseqs_rep_seq.fasta.transdecoder.cds",
                     "04_mmseqs_rep_seq.fasta.transdecoder.gff3",
                     "04_mmseqs_rep_seq.fasta.transdecoder.pep"]

        for file in res_files:
            if self.bindpoint:
                # let's hope this ugly fix works!!
                shutil.move(f"{os.environ['HOME']}/{file}",
                            f"{self.out_pred}/{file}")
            else:
                os.replace(file, f"{self.out_pred}/{file}")
            if file.endswith(".pep"):
                u.clean_deflines(infile=f"{self.out_pred}/{file}",
                                 seq_prefix="prot")

        # Delete the "pipeliner.xxxx.cmds"
        # I can't do this if using singularity container
        if self.bindpoint:
            for file in glob.glob(f"{os.environ['HOME']}/pipeliner.*.cmds"):
                shutil.move(file, f"{self.out_pred}/{os.path.basename(file)}")
                u.remove_file(f"{self.out_pred}/{os.path.basename(file)}")
        else:
            for pipeliner in glob.glob("pipeliner.*.cmds"):
                u.remove_file(pipeliner)

        # Delete temp directories crated by TD "xx.__checkpoints*"
        for dir_to_rm in glob.glob(f"{self.out_long}.*"):
            u.remove_dir(dir_to_rm, other=True)
        return True


if __name__ == '__main__':
    t = TransDecoder()
    t._check_avail()
    t._check_version()
    print(t)
    # remove_pipeliner(glob.glob("pipeliner.*.cmds"))
    # remove_pipeliner(["pipeliner.123456.cmds"])
