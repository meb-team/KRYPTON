# -*- coding: utf-8

import os
import math
import time
import shutil
import subprocess


def create_dir(file_path):
    try:
        os.mkdir(file_path)
    except Exception:
        raise Exception(f"\nThe path you have provided for your output files:"
                        f"\n\n\t'{os.path.abspath(file_path)}'\n\n"
                        f"already is used by a directory. KRYPTON tries to not"
                        f" overwright existing files and directories.")
    return True


def is_file_exists(file_path):
    if not file_path:
        raise Exception("\nNo input file is declared...")
    if not os.path.exists(os.path.abspath(file_path)):
        raise Exception(f"\nNo such file: {os.path.abspath(file_path)}")
    return True


def remove_dir(dir_path, other=None):
    if (os.path.isdir(dir_path)) and (os.path.basename(dir_path) == 'tmp'):
        shutil.rmtree(dir_path)
    elif other:  # This is for future case, not only for tmp dir
        shutil.rmtree(dir_path)
    else:
        raise Exception("The dir can't be deleted. This message is for KRYPTON"
                        " devs only.")
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


def multi_to_single_line_fasta(file_path):
    try:
        is_file_exists(file_path)
    except Exception:
        print("For DEVs: Something went wrong with the file %s" % file_path)
    d = dict()  # From Python 3.6, dict() keep the insertion order

    with open(file_path, 'r') as fi:
        lines = fi.readlines()
        curr_k = ""
        curr_v = ""
        for line in lines:
            line = line.rstrip()
            if line[0] == ">":
                if curr_k != "":
                    # populate the dict with the previous complete sequence
                    d[curr_k] = curr_v
                curr_k = line
                curr_v = ""  # reset of the previous sequence
            else:
                curr_v += line
        d[curr_k] = curr_v  # DO NOT FORGET THE LAST SEQUENCE

    # Write
    with open(file_path + ".oneline.pep", "w") as fo:
        for k, v in d.items():
            print("%s\n%s" % (k, v), file=fo)
    return True


def format_command_trimmomatic(out, bin, mod, r1, r2=None, params=None):
    command = f"java -jar {bin} {mod} "
    if r2:
        command += f"{r1} {r2} {out}/r1.paired.fq {out}/r1.unpaired.fq "
        command += f"{out}/r2.paired.fq {out}/r2.unpaired.fq " \
                   + f"{'' if not params else params}"
    else:
        command += f"{r1} {out}/r1.fq {'' if not params else params}"
    return command


def format_command_trinity(out, r1, r2=None):
    """
    The Trinity parameter `--full_cleanup` change the behaviour of the tool.
    WITHOUT: the result is {self.output}/03_trinity/Trinity.fa
    WITH: Trinity remove all temp files generated and output the results in
        {self.output}/03_trinity.Trinity.fasta
        N.B., with this way, I have to trust Trinity for the dirrectory setup
    """
    command = f"{os.environ['TRINITY_HOME']}/Trinity --seqType fq "\
              + f" --output {out} --CPU 8 --max_memory 64G --full_cleanup "
    if r2:
        command += f"--left {r1} --right {r2}"
    else:
        command += f"--single {r1}"
    return command
