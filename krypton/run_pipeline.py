# -*- coding: utf-8
import os
import time
import math

"""
I have to create a class!
"""


def check_output_exists(file_path):
    if os.path.isdir(file_path):
        raise Exception(f"The path you have provided for your output files "
                        f"('{os.path.abspath(file_path)}') \n"
                        f"already is used by a directory. KRYPTON tries to not"
                        f" overwright existing files and directories.")
    return True


def check_file_exists(file_path):
    if not file_path:
        raise Exception("No input file is declared...")
    if not os.path.exists(os.path.abspath(file_path)):
        raise Exception(f"No such file: {os.path.abspath(file_path)}")
    return True


def parse_arguments(args):
    A = lambda x: args.__dict__[x] if x in args.__dict__ else None
    mode = A('mode')
    output = A('outdir')
    paired = A('paired')
    fwd = A('r1')
    rev = A('r2')
    transcripts = A('transcripts')
    cds = A('cds')
    """ Let's first make KRYPTON running on a regular computer. """
    # bucket_in = A('bucketin')
    # bucket_out = A('bucketout')
    # hpc2 = A('hpc2')

    check_output_exists(output)

    if mode == 'reads':
        if paired:
            if fwd is None or rev is None:
                raise Exception("Mode - READS:\n"
                                "Please provides the paired-end reads via `--r"
                                "1` **and** `--r2`, or use `--single-end`.")
            check_file_exists(fwd)
            check_file_exists(rev)
        else:
            if fwd is None:
                raise Exception("Mode - READS:\n"
                                "Please provides the single-end reads only via"
                                " `--r1`.")
            check_file_exists(fwd)

    if mode == "assembly":
        check_file_exists(transcripts)

    if mode == "cds":
        check_file_exists(cds)

    """
    Just a reminder that I will have to
    add a step to check whether KRYPTON run on a regular
    server or on a HPC cluster.
    """


"""
Here: Several functions to make the funtion 'run_krypton()' clear
and easily comprehensible.
"""


def time_used(timing, step_name):
    """This function prints the time taken by the system to run a step"""
    time_min = int((timing[1] - timing[0]) // 60)  # get the minutes
    time_sec = math.trunc((timing[1] - timing[0]) % 60)  # get the seconds
    print("%s: %smin %ssec" % (step_name, time_min, time_sec))


def run_fastqc(reads, paired, step):
    """
    This function aims to run the tool FastQC on the reads
    It assumes that the file is in the Path
    """
    # check about factQC on single-end reads?
    # create a output_dir

def run_krypton():
    print("KRYPTON is starting. All steps may take a lot of time. "
          "Please be patient...")
    time_global = [time.time()]

    if mode == "reads":
        # FastQC of the raw
        # if paired:
            # run_fastqc([r])

    #
    # directory_KRYPTON = Path(__file__).parent
    # create_dir(dir_output)
    # tutu = 1

    time_global.append(time.time())
    time_used(time_global, "Krypton")

#     # ########## fastqc ##########
#     """
#     Integrate this step into a function as it is used twice. Also make sure
#     to control all parameters for fastqc, like the number of CPUs.
#     """
#     print("Debut de l etape de fastqc sur les reads, cette etape peut \
#             prendre du temps, patience.")
#     debut_timefastqc_raw = time.time()
#     # définit un dossier de sortie pour fastqc
#     output_fastqc_raw = "fastqc_raw"
#     # creer le dossier de sortie et s'y deplace dedans
#     create_dir(output_fastqc_raw)
#     fichier_cible = "*1_1*.zip"
#     command = "fastqc {} {} --outdir ./ --threads 15 \
#                 >raw_fastqc.log 2>&1".format(read_forward, read_backward)
#     check_step(fichier_cible, command)
#     fin_timefastqc_raw = time.time()
#
#     print_time_used(debut_timefastqc_raw, fin_timefastqc_raw, "FastQC_Raw")
#
