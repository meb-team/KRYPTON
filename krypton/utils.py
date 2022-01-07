# -*- coding: utf-8

import os
import math
import time
import subprocess


def create_dir(file_path):
    if os.path.isdir(file_path):
        raise Exception(f"\nThe path you have provided for your output files "
                        f"('{os.path.abspath(file_path)}') \n"
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


def time_used(timing, step_name):
    """This function prints the time taken by the system to run a step"""
    time_min = int((timing[1] - timing[0]) // 60)  # get the minutes
    time_sec = math.trunc((timing[1] - timing[0]) % 60)  # get the seconds
    print("%s: %smin %ssec" % (step_name, time_min, time_sec))


def run_command(command, capture_out=True, log=None, step=None):
    time_cmd = [time.time()]
    subprocess.run(command.split(), capture_output=capture_out, stdout=log,
                   stderr=subprocess.STDOUT)
    time_cmd.append(time.time())
    print(time_used(time_cmd), step)
    return True
