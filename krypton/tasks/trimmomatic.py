# -*- coding: utf-8

import sys
import glob
import subprocess
import krypton.utils as u

"""
Add something to test the presence of Trimmomatic in the PATH
"""


def check_version(path=None):
    with_java = False
    if not path:
        try:
            subprocess.check_output(['trimmomatic', '-version'],
                                    encoding='utf-8')
        except subprocess.CalledProcessError:
            with_java = True
        else:
            return True

    elif with_java:
        try:
            subprocess.check_output(['java', '-jar', path, '-version'],
                                    encoding='utf-8')
        except subprocess.CalledProcessError:
            try:  # Is java present?
                subprocess.check_output(['java', '-version'], encoding='utf-8')
            except subprocess.CalledProcessError:
                print("KRYPTON did not found Java on your machine. Please "
                      "install it for runnning Trimmomatic.\nKRYPTON ends")
                sys.exit(1)
            else:
                print("KRYPTON did not found the Trimmomatic JAR file.\n"
                      "Please check the path you provided to `--trimmomatic` "
                      "is correct. Note, it MUST includes the executable.\n"
                      "KRYPTON ends")
                sys.exit(1)


class Trimmomatic():

    def __init__(self, raw=None, project=None, threads=None, exec=None):
        self.max_threads = threads
        self.output = project + "/01_trimmomatic"
        self.exec = exec
        u.create_dir(self.output)

    def format_command(self, mod, r1, r2=None, params=None):
        command = "trimmomatic" if not self.exec else f"java -jar {self.exec}"
        command += f" {mod} -threads {self.max_threads} "
        if r2:
            command += f"{r1} {r2} {self.output}/r1.paired.fq " +\
                       f"{self.output}/r1.unpaired.fq {self.output}" +\
                       f"/r2.paired.fq {self.output}/r2.unpaired.fq "
        else:
            command += f"{r1} {self.output}/r1.fq "

        command += f"{'' if not params else params}"
        return command


def clean(project):
    for file in glob.glob(f"{project}/01_trimmomatic/*.fq"):
        u.remove_file(file)
    return True
