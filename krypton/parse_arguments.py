# -*- coding: utf-8
import os


def check_output_exists(file_path):
    if os.path.isdir(file_path):
        raise Exception(f"The path you have provided for your output files "
                        f"('{os.path.abspath(file_path)}') \n"
                        f"already is used by a directory. KRYPTON tries to not"
                        f" overwright existing files and directories.")


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
                                "Please provides the paired-end reads via "
                                "`--r1` **and** `--r2`, or use `--single-end`.")
        else:
            if fwd is None:
                raise Exception("Mode - READS:\n"
                                "Please provides the single-end reads only via"
                                " `--r1`.")
        # check files for reads

    if mode == "assembly":
        tutu = 1
        # check file for transcripts
    if mode == "cds":
        titi = 2
        # check file of CDS
