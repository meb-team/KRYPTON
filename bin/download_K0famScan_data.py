#!/usr/bin/env python
# -*- coding: utf-8

import os
import time
import argparse
import urllib.request

import krypton.utils as u

if __name__ == '__main__':
    abs_path = os.path.dirname(os.path.abspath(__name__))

    parser = argparse.ArgumentParser(description="Download a K0 list and HMM "
                                     "profiles for K0famScan",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--dest', help='Path to store the K0 list and HMM '
                        'profiles used by K0famScan. The directory will be '
                        'created if it does not exist.\nDisk usage: ~6.5GB.\n'
                        'Default: within the KRYPTON install directory.',
                        metavar='')

    args = parser.parse_args()

    url_base = 'https://www.genome.jp/ftp/db/kofam'
    files = ['ko_list.gz', 'profiles.tar.gz']

    out = abs_path + "/ressources/KEGG_data" if not args.dest \
            else args.dest.rstrip("/")
    try:
        u.check_dir_exists(out)
    except Exception:
        u.create_dir(out)

    print(f"Start to download K0famScan files in {out} ...")

    for file in files:
        urllib.request.urlretrieve(url_base + '/' + file, out + '/' + file)
        print(f"\t{file}: OK")
        time.sleep(2)

    u.run_command(command=f"gunzip {out}/{files[0]}",
                  step=f"Unzipping {files[0]}")

    u.run_command(command=f"tar -C {out} -zxf {out}/{file}",
                  step="Decompressing HMM profiles")
