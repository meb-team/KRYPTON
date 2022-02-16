#!/usr/bin/env python3
# -*- coding: utf-8

import time
import argparse
import urllib.request

import krypton.utils as u

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download a K0 list and HMM "
                                     "profiles for K0famScan",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('dest', help='Path to store the K0 list and HMM '
                        'profiles used by K0famScan. The directory will be '
                        'created if it does not exist.\nDisk usage: ~6.5GB.\n',
                        metavar='PATH')

    args = parser.parse_args()

    url_base = 'https://www.genome.jp/ftp/db/kofam'
    files = ['ko_list.gz', 'profiles.tar.gz']

    try:
        u.check_dir_exists(args.dest)
    except Exception:
        u.create_dir(args.dest)

    print(f"Start to download K0famScan files in {args.dest} ...")

    for file in files:
        urllib.request.urlretrieve(url_base + '/' + file,
                                   args.dest + '/' + file)
        print(f"\t{file}: OK")
        if file.endswith(".tar.gz"):
            u.run_command(command=f"tar -C {args.dest} -zxf {args.dest}/{file}",
                          step=f"Decompressing {file}")
            u.remove_file(args.dest + "/" + file)
        else:
            u.run_command(command=f"gunzip {args.dest}/{file}",
                          step=f"Unzipping {file}")
        time.sleep(2)
