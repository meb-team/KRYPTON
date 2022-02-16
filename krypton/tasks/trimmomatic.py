# -*- coding: utf-8

import sys
import glob
import subprocess as s
import krypton.utils as u


def check_version(path=None, mode=None):
    with_java = False
    if not path:
        print("\t1")
        if _check_conda():
            print("Conda ok")
            return f"trimmomatic {mode}"
        elif _check_apt():
            print("APT ok")
            return f"Trimmomatic{mode}"
        else:
            print("Need to check with java path")
            with_java = True
    elif with_java:
        print("start with java")
        try:
            s.check_output(['java', '-jar', path, '-version'], encoding='utf-8')
        except s.CalledProcessError:
            try:  # Is java present?
                print("is java present?")
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
        print("TRY conda")
        print(s.check_output(['trimmomatic', '-version'], encoding='utf-8',
                             stderr=s.STDOUT), shell=True)
        print("TRY conda - after")

    except s.CalledProcessError:
        return False
    return True


def _check_apt():
    try:
        print("TRY apt")
        s.check_output(['TrimmomaticPE', '-version'], encoding='utf-8')
    except s.CalledProcessError:
        return False
    return True


def clean(project):
    print("Removing Trimmomatic cleaned reads")
    for file in glob.glob(f"{project}/01_trimmomatic/*.fq"):
        u.remove_file(file)
    return True


class Trimmomatic():

    def __init__(self, r1, params, raw=None, project=None, threads=None,
                 exec=None, r2=None):
        self.r1 = r1
        self.r2 = r2
        self.max_threads = threads
        self.output = project + "/01_trimmomatic"
        self.mode = "PE" if self.r2 else "SE"
        self.exec = check_version(path=exec, mode=self.mode)
        self.params = params
        u.create_dir(self.output)

    def trimmomatic(self, step):
        command = f"{self.exec} -threads {self.max_threads} "
        if self.mode == "PE":
            command += f"{self.r1} {self.r2} " + \
                       f"{self.output}/r1.paired.fq " + \
                       f"{self.output}/r1.unpaired.fq " + \
                       f"{self.output}/r2.paired.fq " + \
                       f"{self.output}/r2.unpaired.fq " + \
                       f"{self.params}"
        else:
            command += f"{self.r1} {self.output}/r1.fq {self.params}"

        with open(f"{self.output}/01_logs.log", "w") as log:
            u.run_command(command=command, log=log, step=step)
        return True
