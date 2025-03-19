# -*- coding: utf-8

import os
import sys
import glob
import subprocess as s
import krypton.utils as u


def check_version(path=None, mode=None):
    """DEPRECATED
    Function that checked the installed version for Trimomatic
    But I am not sure it was working well..."""
    with_java = False
    if not path:
        if _check_conda():
            return f"trimmomatic {mode}"
        elif _check_apt():
            # With APT, TrimmomaticSE or TrimmomaticPE
            return f"Trimmomatic{mode}"
        else:
            with_java = True
    elif with_java:
        try:
            s.check_output(['java', '-jar', path, '-version'],
                           encoding='utf-8')
        except (s.CalledProcessError, FileNotFoundError):
            try:  # Is java present?
                s.check_output(['java', '-version'], encoding='utf-8')
            except (s.CalledProcessError, FileNotFoundError):
                print("KRYPTON did not found Java on your machine. Please "
                      "install it for runnning Trimmomatic.\nKRYPTON ends")
                sys.exit(1)
            else:
                print("KRYPTON did not found the Trimmomatic JAR file.\n"
                      "Please check the path you provided to `--trimmomatic` "
                      "is correct. Note, it MUST includes the executable.\n"
                      "KRYPTON ends")
                sys.exit(1)
        return f"java -jar {path} {mode}"


def _check_conda():
    try:
        os.environ['CONDA_PREFIX']  # raise a KeyError if not found
    except (s.CalledProcessError, KeyError, FileNotFoundError):
        return False
    return True


def _check_apt():
    try:
        s.check_output(['TrimmomaticPE', '-version'], encoding='utf-8')
    except (s.CalledProcessError, FileNotFoundError):
        return False
    return True


def clean(project):
    print("Removing Trimmomatic cleaned reads")
    for file in glob.glob(f"{project}/01_trimmomatic/*.fq"):
        u.remove_file(file)
    return True


class Trimmomatic():
    """A Class to generate and execute trimmomatic for PE or SE data"""
    def __init__(self, r1, params, project=None, threads=None, r2=None):
        self.r1 = r1
        self.r2 = r2
        self.max_threads = threads
        self.output = project + "/01_trimmomatic"
        self.mode = "PE" if self.r2 else "SE"
        self.params = params
        u.create_dir(self.output)

    def trimmomatic(self, step):
        """Generate the command and run it"""
        if self.mode == "PE":
            command = f"trimmomatic PE -threads {self.max_threads} " + \
                      f"{self.r1} {self.r2} " + \
                      f"{self.output}/r1.paired.fq " + \
                      f"{self.output}/r1.unpaired.fq " + \
                      f"{self.output}/r2.paired.fq " + \
                      f"{self.output}/r2.unpaired.fq " + \
                      f"{self.params}"
        else:
            command = f"trimmomatic SE -threads {self.max_threads} " + \
                      f"{self.r1} {self.output}/r1.fq {self.params}"

        with open(f"{self.output}/01_logs.log", "w",
                  encoding="utf-8") as log:
            u.run_command(command=command, log=log, step=step)
        return True
