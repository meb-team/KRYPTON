#!/usr/bin/env python3
# -*- coding: utf-8
"""Download data from KEGG to run 'KOfamScan"""

import time
import argparse
import urllib.request

import progressbar

import krypton.utils as u


class MyProgressBar():
    """A progress bar for urlretrieve()
    source : https://stackoverflow.com/a/53643011 """
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download a K0 list and HMM "
                                     "profiles for K0famScan",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--out', help='Path to store the K0 list and HMM '
                        'profiles used by K0famScan.\nThe directory will be '
                        'created if it does not exist.\nDisk usage: ~6.5GB.\n'
                        '\nIt can be extremly long to download the files'
                        "\nDefault is working directory, '.'",
                        metavar='', default=".")

    parser.add_argument("--test", help="A test download (SwissProt)",
                        action='store_true', default=False)

    args = parser.parse_args()

    URL_BASE = 'https://www.genome.jp/ftp/db/kofam'
    files = ['ko_list.gz', 'profiles.tar.gz']

    try:
        u.check_dir_exists(args.out)
    except Exception:
        u.create_dir(args.out)

    if args.test:
        # Propose to test to download a file
        print("Try to download Swiss-Prot fasta file (~90Mb)...\n")
        TEST_URL = "https://ftp.uniprot.org/pub/databases/uniprot/" \
                   "current_release/knowledgebase/complete/"
        TEST_FILE = "uniprot_sprot.fasta.gz"

        urllib.request.urlretrieve(TEST_URL + '/' + TEST_FILE,
                                   TEST_FILE,
                                   MyProgressBar())

    else:
        # Main purpose of the script, download files from KEGG
        print(f"Start to download K0famScan files in {args.out} ...")

        for file in files:
            try:
                # Use the Progress bar
                urllib.request.urlretrieve(URL_BASE + '/' + file,
                                        args.out + '/' + file,
                                        MyProgressBar())

            except Exception:
                # Too bad, the server does not send informations,
                # so no progressBar
                urllib.request.urlretrieve(URL_BASE + '/' + file,
                                        args.out + '/' + file)

            print(f"\t{file}: OK")

            if file.endswith(".tar.gz"):
                u.run_command(command=f"tar -C {args.out} -zxf {args.out}/{file}",
                              step=f"Decompressing {file}")
                u.remove_file(args.out + "/" + file)

            else:
                u.run_command(command=f"gunzip {args.out}/{file}",
                              step=f"Unzipping {file}")
            time.sleep(2)
