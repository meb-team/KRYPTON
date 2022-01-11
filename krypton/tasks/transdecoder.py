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


if __name__ == '__main__':
    check_version()
