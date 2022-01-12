# -*- coding: utf-8

import os
import glob
import subprocess
from subprocess import CalledProcessError

import krypton.utils as u


class TransDecoder():

    def __init__(self):
        self.required_version = "5.5.0"
        self._check_avail()
        self._check_version()

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

    def format_longorf(self, transcrits_clust, outdir, min_size=None):
        command = f"TransDecoder.LongOrfs --output_dir {outdir}"\
                  + f" -t {transcrits_clust}"
        if min_size:
            command += f" -m {min_size}"
        return command

    def format_predict(self, transcrits_clust, pred_input, pfam=None,
                       pfam_res=None):
        command = f"TransDecoder.Predict --output_dir {pred_input}"\
                  + f" -t {transcrits_clust}"
        if pfam:
            """
            It can enter here ONLY in the case where the user aksed for the
            Pfam annotation here.
            It is possible to have a similar approach from BLAST
            """
            command += f" --retain_pfam_hits {pfam_res}"

        return command

    def clean(self, dest, transcripts, from_long):
        """
        Clean the mess Transdecoder is producing
        Giving this issue
        (https://github.com/TransDecoder/TransDecoder/issues/108)
        I guess it would be better for me to move the result files myself, not
        waiting for a TransDecoder update.
        """

        for file in glob.glob(f"{os.path.basename(transcripts)}*"):
            os.replace(file, f"{dest}/{file}")
        self.remove_pipeliner(glob.glob("pipeliner.*.cmds"))

        for dir_to_rm in glob.glob(f"{from_long}.*"):
            u.remove_dir(dir_to_rm, other=True)

    def remove_pipeliner(self, file_path):
        for file in file_path:
            try:
                os.remove(file)
            except FileNotFoundError:
                print("Message for KRYPTON devs:\n",
                      f"Cannot remove the file {os.path.abspath(file)}",
                      sep='')
        return True


if __name__ == '__main__':
    t = TransDecoder()
    t._check_avail()
    t._check_version()
    print(t)
    # remove_pipeliner(glob.glob("pipeliner.*.cmds"))
    # remove_pipeliner(["pipeliner.123456.cmds"])
