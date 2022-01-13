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


def read_fasta(file_path):
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
    return d


def multi_to_single_line_fasta(file_path):
    d = read_fasta(file_path)
    # Write
    with open(file_path + ".oneline.pep", "w") as fo:
        for k, v in d.items():
            print("%s\n%s" % (k, v), file=fo)
    return True


def simplify_seq_id(count, string_size):
    """
    input a number, eg 361, return a string of size 'size'
    with X leading 0s. Eg 000000361 for num=361, size=9
    """
    if len(str(count)) <= string_size:
        return ("0" * (string_size - len(str(count)))) + str(count)
    else:
        raise Exception("For DEVs: You did not expected some many sequences..."
                        + f"There are at least {count} sequences")


def clean_deflines(infile, seq_prefix, name_size=9):
    count = 0
    with open(infile, "r") as fi:
        with open(infile + ".clean_defline.fa", "w") as fo:
            with open(infile + ".corres_tab.tab", "w") as corres:
                lines = fi.readlines()
                for line in lines:
                    line = line.rstrip()
                    if line[0] == ">":
                        new_s = f">{seq_prefix}_{simplify_seq_id(count, name_size)}"
                        print(new_s, file=fo)
                        print(line[1:], new_s[1:], sep="\t", file=corres)
                        count += 1
                    else:
                        print(line, file=fo)
    return True
