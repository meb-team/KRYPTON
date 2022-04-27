#!/usr/bin/env python3
# -*- coding: utf-8

import os
import sys
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

    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
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
    groupG = parser.add_argument_group('KO annotation')
    groupH = parser.add_argument_group('General options')
    groupA.add_argument('--mode', help='Pipeline mode, a.k.a the step from '
                        'which the pipeline starts', default="reads", type=str,
                        choices=['reads', 'assembly', 'cds'])
    groupA.add_argument('--out', help='Prefix for the output directory',
                        dest='outdir', metavar="OUT_DIR", required=True)
    # groupA.add_argument('--overwrite', help='Overwrite the output if it '
    #                     'exists. Do you really want to use this feature?'
    #                     ' -- NOT YET IMPLEMENTED', action='store_true',
    #                     default=False)
    groupB.add_argument('--single-end', help='For Single-End reads, use this '
                        'option and provide the dataset through `--r1`',
                        action='store_false', dest='paired', default=True)
    groupB.add_argument('--r1', help='The first read of the pair, in FASTQ'
                        ' (foo_R1.fq[.gz]).', metavar="R1")
    groupB.add_argument('--r2', help='The second read of the pair, in FASTQ'
                        ' (foo_R2.fq[.gz]).', metavar="R2")
    groupB.add_argument('--trimmomatic', help="If APT or Conda Trimmomatic "
                        "is installed, forget this option.\nFor other "
                        "instal:\n\tPATH/TO/trimmomatic-<version>.jar",
                        metavar="PATH")
    groupC.add_argument('--transcripts', help='File with ASSEMBLED TRANSCRIPTS'
                        ', in FASTA (foo.fa[.gz])', metavar="FILE")
    groupC.add_argument('--min-protein-len', help="Minimal protein length"
                        " for TransDecoder.LongOrfs. Default is 100 AA",
                        dest="min_prot_len", metavar="SIZE", default=100)
    groupD.add_argument('--cds', help='File with TRANSLATED CDS, in FASTA '
                        '(foo.fa[.gz])', metavar="FILE")
    groupD.add_argument('--no-cds-cluster', help='Turn OFF the clustering step'
                        ' for the CDS', action="store_true", default=False,
                        dest="no_cds_cluster")
    # groupE.add_argument('--bucket-in', help='Name of the bucket used to read'
    #                     ' data from. This option is required to run KRYPTON on'
    #                     ' the HPC2 cluster', metavar="BUCKET_IN")
    # groupE.add_argument('--bucket-out', help='Name of the bucket used to store'
    #                     ' data in. This option is required to run KRYPTON on'
    #                     ' the HPC2 cluster', metavar="BUCKET_OUT")
    # groupE.add_argument('--run-on-HPC', help='Turn on this option when KRYPTON'
    #                     ' is meant to be run on a HPC cluster -- WIP',
    #                     action='store_true', default=False, dest='hpc2')
    groupF.add_argument('--mmseqs-annot', help='Turn ON the annotation with '
                        'MMseqs2 and a database.', action="store_true",
                        default=False, dest='mmseq_annot')
    groupF.add_argument('--mmseqs-db', help='The name of a database provided '
                        'by MMseqs2 (the list is present at '
                        'https://github.com/soedinglab/MMseqs2/wiki#downloading-databases) '
                        '\n**OR**\nPath to a fa,fasta,fq,fastq,pep[.gz] '
                        'file.\n#####\nDefault:\n\t- the database is setup '
                        'within the output directory. To store the database '
                        'elsewhere on the disk, provide a path with '
                        '`--mmseqs-db-path`\n\t- If nothing is provided, '
                        'KRYPTON uses the UniProtKB/Swiss-Prot database.',
                        dest="mmseq_db", metavar="",)
    groupF.add_argument('--mmseqs-db-path', help='Path to an existing database'
                        '\n**OR**\nPath to a directory to store the database '
                        'passed to `--mmseqs-db`',
                        dest='mmseq_db_path', metavar="")
    groupG.add_argument('--ko-annot', help='PATH to a directory containing '
                        '`ko_list` & `profiles` for K0famScan.\nKRYPTON '
                        'provides a simple script to download them:\n\t- '
                        'KRYPTON_download_K0famScan_data.py\n',
                        dest="ko_annot", metavar="PATH")
    groupH.add_argument('-t', help='Maximum number of threads that KRYPTON '
                        'can use.', dest='threads')
    groupH.add_argument('--mem', help='Maximum amount of RAM - in GB - that '
                        'KRYPTON can use, eg 64 to ask for 64GB of RAM')
    groupH.add_argument('--bindpoint', help='To use with a Singularity '
                        'container!!!\nThe binding point present within the '
                        'container, eg /data.\nThis is For Transdecoder as the'
                        ' tool outputs its results in CWD...', metavar="PATH")
    groupH.add_argument('--assembly-only', help='Just assembles the '
                        'transcripts and stops after.\t Dafault = False',
                        action="store_true", default=False)

    if len(sys.argv) == 1:  # In the case where nothing is provided
        # parser.print_help(file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    try:
        """
        For the moment, let's try to make KRYPTON run on a regular computer.
        I will see later to implement the stuff related to
            --bucketin / -- bucketout / --run-on-hpc2
        """
        test = k.Krypton(args=args)
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
