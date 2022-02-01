# -*- coding: utf-8

import sys
import krypton.utils as u


def ko_check_user_files(file_path):
    """ check that user provided the correct path"""
    try:
        u.is_file_exists(file_path.rstrip('/') + '/ko_list')
        u.check_dir_exists(file_path.rstrip('/') + '/profiles')
    except Exception:
        print(f'\nKRYPTON cannot find the file `{file_path}/ko_list` or the '
              f'directory `{file_path}/profiles/`\nPlease make sur to '
              'provide the right PATH through `--kegg-ko-ref`\n'
              '~~~~~KRYPTON stops~~~~~ ')
        sys.exit(1)
    return True


class KO_annot():
    def __init__(self, threads=None, project=None, ko_files=None,
                 proteins=None):
        self.max_threads = threads
        self.output = project + "/" + '09_ko_annot'
        self.input = proteins
        self.ko_list = ko_files + '/ko_list'
        self.profiles = ko_files + '/profiles'
        self.tmp = self.output + "/tmp"
        u.create_dir(self.output)

    def run_kofamscan(self, format=None, step=None):
        command = f'exec_annotation -o {self.output}/09_kofam_results.tsv ' +\
                  f'--format {format} --ko-list {self.ko_list} --profile ' +\
                  f'{self.profiles} --cpu {self.max_threads} ' +\
                  f'--tmp-dir {self.tmp} {self.input}'
        with open(f"{self.output}/09_kofam_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True
