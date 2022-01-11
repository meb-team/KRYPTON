# -*- coding: utf-8

import os
import glob
import subprocess
from subprocess import CalledProcessError

import krypton.utils as u


def check_version():
    try:
        subprocess.run(["TransDecoder.LongOrfs", "--version"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except (FileNotFoundError, CalledProcessError) as e:
        if e == 'FileNotFoundError':
            print("The excecutable for TransDecoder.LongOrfs is not present",
                  "in your PATH")
        else:
            print("One of the parameter provided to TransDecoder.LongOrfs is",
                  "wrong.")
        return False
    return True


def format_longorf(transcrits_clust, outdir, min_size=None):
    command = f"TransDecoder.LongOrfs --output_dir {outdir}"\
              + f" -t {transcrits_clust}"
    if min_size:
        command += f" -m {min_size}"

    return command


def format_predict(transcrits_clust, pred_input, pfam=None, pfam_res=None):
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


def clean(dest, transcripts, from_long):
    """
    Clean the mess Transdecoder is producing
    Giving this issue (https://github.com/TransDecoder/TransDecoder/issues/108)
    I guess it would be better for me to move the result files myself, not
    waiting for a TransDecoder update.
    """

    for file in glob.glob(f"{os.path.basename(transcripts)}*"):
        os.replace(file, f"{dest}/{file}")
    remove_pipeliner(glob.glob("pipeliner.*.cmds"))

    for dir_to_rm in glob.glob(f"{from_long}.*"):
        u.remove_dir(dir_to_rm, other=True)


def remove_pipeliner(file_path):
    for file in file_path:
        try:
            os.remove(file)
        except FileNotFoundError:
            print("Message for KRYPTON devs:\n",
                  f"Cannot remove the file {os.path.abspath(file)}", sep='')
    return True


if __name__ == '__main__':
    check_version()
    # remove_pipeliner(glob.glob("pipeliner.*.cmds"))
    # remove_pipeliner(["pipeliner.123456.cmds"])
