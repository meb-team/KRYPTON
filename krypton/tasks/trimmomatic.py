# -*- coding: utf-8

import sys
import glob
import subprocess as s
import krypton.utils as u


def check_version(path=None, mode=None):
    with_java = False
    if not path:
        if _check_conda():
            return f"trimmomatic {mode}"
        elif _check_apt():
            return f"Trimmomatic{mode}"
        else:
            with_java = True
    elif with_java:
        try:
            s.check_output(['java', '-jar', path, '-version'], encoding='utf-8')
        except s.CalledProcessError:
            try:  # Is java present?
                s.check_output(['java', '-version'], encoding='utf-8')
            except s.CalledProcessError:
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
        s.check_output(['trimmomatic', '-version'], encoding='utf-8')
    except s.CalledProcessError:
        return False
    return True


def _check_apt():
    try:
        s.check_output(['TrimmomaticPE', '-version'], encoding='utf-8')
    except s.CalledProcessError:
        return False
    return True


def clean(project):
    for file in glob.glob(f"{project}/01_trimmomatic/*.fq"):
        u.remove_file(file)
        print("Removing Trimmomatic clean reads...")
        return True


class Trimmomatic():

    def __init__(self, r1, params, raw=None, project=None, threads=None,
                 exec=None, r2=None):
        self.max_threads = threads
        self.output = project + "/01_trimmomatic"
        self.mode = "PE" if r2 else "SE"
        self.exec = check_version(path=exec, mode=self.mode)
        self.params = params
        u.create_dir(self.output)

    def trimmomatic(self, step):
        command = f"{self.exec} -threads {self.max_threads} "
        if self.mode == "PE":
            command += f"{self.r1} {self.r2} {self.output}/r1.paired.fq " +\
                       f"{self.output}/r1.unpaired.fq {self.output}" +\
                       f"/r2.paired.fq {self.output}/r2.unpaired.fq " + \
                       f"{self.params}"
        else:
            command += f"{self.r1} {self.output}/r1.fq {self.params}"

        with open(f"{self.output}/01_logs.log", "w") as log:
            u.run_command(comcommand=command, log=log, step=step)
