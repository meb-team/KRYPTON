# -*- coding: utf-8

import os
import math
import time
import subprocess


def create_dir(file_path):
    if os.path.isdir(file_path):
        raise Exception(f"\nThe path you have provided for your output files:"
                        f"\n\n\t'{os.path.abspath(file_path)}'\n\n"
                        f"already is used by a directory. KRYPTON tries to not"
                        f" overwright existing files and directories.")
    else:
        os.mkdir(file_path)
    return True


def is_file_exists(file_path):
    if not file_path:
        raise Exception("\nNo input file is declared...")
    if not os.path.exists(os.path.abspath(file_path)):
        raise Exception(f"\nNo such file: {os.path.abspath(file_path)}")
    return True


def time_used(timing, step_name="Unknown step"):
    """This function prints the time taken by the system to run a step"""
    time_min = int((timing[1] - timing[0]) // 60)  # get the minutes
    time_sec = math.trunc((timing[1] - timing[0]) % 60)  # get the seconds
    print("%s: %smin %ssec" % (step_name, time_min, time_sec))


def run_command(command, capture_out=False, log=None, step=None):
    time_cmd = [time.time()]
    subprocess.run(command.split(), capture_output=capture_out, stdout=log,
                   stderr=subprocess.STDOUT)
    time_cmd.append(time.time())
    time_used(time_cmd, step)
    return True


def format_command_trimmomatic(out, bin, mod, r1, r2=None, params=None):
    command = f"java -jar {bin} {mod} "
    if mod == "PE":
        command += f"{r1} {r2} {out}/r1.paired.fq {out}/r1.unpaired.fq "
        command += f"{out}/r2.paired.fq {out}/r2.unpaired.fq " \
                   + f"{'' if not params else params}"
    else:
        command += f"{r1} {out}/r1.fq {'' if not params else params}"
    return command


def format_command_fastqc(out, r1, r2=None):
    command = f"fastqc --outdir {out}"
    command = f"{command} {r1}" if not r2 else f"{command} {r1} {r2}"
    return command
