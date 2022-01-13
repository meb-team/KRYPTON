#!/usr/bin/env python
# -*- coding: utf-8

# import os
# import re
import sys
# import time
# import math
# from pathlib import Path
# import subprocess
# from pathlib import Path
import argparse

import krypton.run_pipeline as k

__description__ = 'Run the pipeline KRYPTON, for transcriptome'\
                ' assembly and annotation'
"""
Damien

for the package:
    - https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html

Tasks to do:
    - [X] Use the module argparse for the parameters

    - [ ] use "with open(xxx, ?) as yyy" to read files.
        It is much more efficient
__authors__ = ['bmilisavljevic', 'AnthonyAUCLAIR', 'd-courtine']

- outdir
- input data --> depend on the mode

- print a log message at the start of the pipeline, with the mode, etc.
"""

"""
# On active un environnement conda avec python3.5 installe prealablement
#os.system("PATHCONDA=$(conda info | grep -i 'base environment' \
            | awk -F" " '{print $4}')")
#os.system("source $PATHCONDA'/etc/profile.d/conda.sh'")
#os.system("conda activate snakes")
#os.system("source activate snakes")
"""
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__description__)
    groupA = parser.add_argument_group('Mandatory arguments')
    groupB = parser.add_argument_group('Mode - READS', description="From reads"
                                       " up to the annotation. Use the BASH "
                                       " environment variable `TRINITY_HOME` "
                                       "to point the directory containing the"
                                       " executable for Trinity.")
    groupC = parser.add_argument_group('Mode - ASSEMBLY')
    groupD = parser.add_argument_group('Mode - CDS')
    groupE = parser.add_argument_group('KRYPTON run on HPC')
    groupF = parser.add_argument_group('MMseqs2 options')
    groupA.add_argument('--mode', help='Pipeline mode, a.k.a the step from '
                        'which the pipeline is run', default="reads", type=str,
                        choices=['reads', 'assembly', 'cds'])
    groupA.add_argument('--out', help='Prefix for the output directory',
                        dest='outdir', metavar="OUT_DIR", required=True)
    groupA.add_argument('--overwrite', help='Overwrite the output if it '
                        'exists. Do you really want to use this feature?'
                        ' -- NOT YET IMPLEMENTED', action='store_true',
                        default=False)
    groupB.add_argument('--single-end', help='In case of **Single-End reads**,'
                        ' use this option and provide `--r1` only.',
                        action='store_false', dest='paired', default=True)
    groupB.add_argument('--r1', help='The first read of the pair, in FASTQ'
                        ' (foo_R1.fq[.gz]) format.', metavar="")
    groupB.add_argument('--r2', help='The second read of the pair, in FASTQ'
                        ' (foo_R2.fq[.gz]) format.', metavar="")
    groupB.add_argument('--trimmomatic', help="Path to the executable "
                        '`trimmomatic-<version>.jar`', metavar="",
                        default="/usr/share/java/trimmomatic-0.39.jar")
    groupC.add_argument('--transcripts', help='A file containing transcrits'
                        ' already assembled, in FASTA format (bar.fa[.gz])',
                        metavar="")
    groupD.add_argument('--cds', help='File with the cds extracted from a set'
                        ' of transcripts, in FASTA format (baz.fa[.gz])',
                        metavar="")
    groupE.add_argument('--bucketin', help='Name of the bucket used to read'
                        ' data from. This option is required to run KRYPTON on'
                        ' the HPC2 cluster', metavar="BUCKET_IN")
    groupE.add_argument('--bucketout', help='Name of the bucket used to store'
                        ' data in. This option is required to run KRYPTON on'
                        ' the HPC2 cluster', metavar="BUCKET_OUT")
    groupE.add_argument('--run-on-HPC', help='Turn on this option when KRYPTON'
                        ' is meant to be run on a HPC cluster -- WIP',
                        action='store_true', default=False, dest='hpc2')
    groupF.add_argument('--mmseqs-search-db', help=' One of 1) Path to an'
                        'existing MMseqs2 database (Fast); 2) The name of a '
                        'database provided by MMseqs2; a list is present here'
                        'https://github.com/soedinglab/MMseqs2/wiki#downloading-databases'
                        '(Can be long and take lot of disk space, eg UniRef90'
                        '~=70GB; 3) Path to a FastA/Q[.gz] file, with the follo'
                        'wing extensions: .fa .fasta .fq .fastq in .gz or not.'
                        '---- Default = UniRef100', dest="mmseq_db")

    """UniRef90 take about 70GB of diskspace"""

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    try:
        """
        For the moment, let's try to make KRYPTON run on a regular computer.
        I will see later to implement the stuff related to
            --bucketin / -- bucketout / --run-on-hpc2
        """
        test = k.Krypton(args)
        test.run_krypton()
        # Here run the process, based on the arguments

    except Exception as e:
        print(e)
        sys.exit(1)

"""
from initialize.py import nom_base_donnees_reference
from initialize.py import base_donnees_reference

annotation_Pfam = sys.argv[5]

if annotation_Pfam == "Pfam" :
        from initialize.py import base_reference_Pfam

if len(sys.argv) == 6 :
        nom_base_donnees_reference = sys.argv[5]
        base_donnees_reference = sys.argv[6]

if len(sys.argv) == 7 :
        nom_base_donnees_reference = sys.argv[6]
        base_donnees_reference = sys.argv[7]
"""
