# -*- coding: utf-8

import subprocess
from subprocess import CalledProcessError


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


if __name__ == '__main__':
    check_version()
