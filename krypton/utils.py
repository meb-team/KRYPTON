# -*- coding: utf-8

import os
import sys
import math
import time
import shutil
import subprocess


def create_dir(file_path):
    try:
        os.makedirs(file_path)
    except FileExistsError:
        # raise Exception(f"\nThe path you have provided for your output files:"
        #                 f"\n\n\t'{os.path.abspath(file_path)}'\n\n"
        #                 f"already is used by a directory. KRYPTON tries to not"
        #                 f" overwright existing files and directories.")
        print("\n\nImpossible to create the directory %s\n"
              % os.path.abspath(file_path), "KRYPTON can't reach it or it is",
              " already present.\nKRYPTON is terminating.\n", sep='')
        sys.exit(1)
    return True


def is_file_exists(file_path):
    if not file_path:
        raise Exception("\nNo input file is declared...")
    if not os.path.exists(os.path.abspath(file_path)):
        raise Exception("\n\nKRYPTON cannot reach the file: "
                        f"{os.path.abspath(file_path)}\n")
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


def remove_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print("Message for KRYPTON devs:\n",
              f"Cannot remove the file {os.path.abspath(file_path)}", sep='')
    return True


def check_seq_file_extension(file_path):
    _ext_ok = ('.fa', '.fasta', '.fq', '.fastq', '.pep')
    if file_path.lower().endswith('.gz'):
        if file_path.lower()[:-3].endswith(_ext_ok):
            return True
    elif file_path.lower().endswith(_ext_ok):
        return True
    else:
        return False


def check_dir_exists(dir_path, param=None):
    if not os.path.isdir(dir_path):
        raise Exception('KRYPTON cannot access the path provided to the '
                        f'parameter "{param}". This directory MUST exists.')
    return True


def full_check_file(file_path):
    if is_file_exists(file_path) and check_seq_file_extension(file_path):
        return True
    else:
        return False


def time_used(timing, step=None):
    """This function prints the time taken by the system to run a step"""
    time_min = int((timing[1] - timing[0]) // 60)  # get the minutes
    time_sec = math.trunc((timing[1] - timing[0]) % 60)  # get the seconds
    if not step:
        print("%smin %ssec" % (time_min, time_sec))
    else:
        print("%s: %smin %ssec" % (step, time_min, time_sec))
    return True


def run_command(command, log=subprocess.DEVNULL, step=None):
    time_cmd = [time.time()]
    subprocess.run(command.split(), stdout=log, stderr=subprocess.STDOUT)
    time_cmd.append(time.time())
    time_used(time_cmd, step=step)
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
