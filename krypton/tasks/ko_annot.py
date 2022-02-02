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
    def __init__(self, threads=1, project=None, ko_files=None,
                 proteins=None, new_dir=True):
        self.max_threads = threads
        self.output = project + "/" + '09_ko_annot'
        self.input = proteins
        self.ko_list = '' if not ko_files else ko_files + '/ko_list'
        self.profiles = '' if not ko_files else ko_files + '/profiles'
        self.tmp = self.output + "/tmp"
        self.results = self.output + '/09_kofam_results.tsv'
        if new_dir:
            u.create_dir(self.output)

    def run_kofamscan(self, format=None, step=None):

        command = f'exec_annotation -o {self.results} ' +\
                  f'--format {format} --ko-list {self.ko_list} --profile ' +\
                  f'{self.profiles} --cpu {self.max_threads} ' +\
                  f'--tmp-dir {self.tmp} {self.input}'
        with open(f"{self.output}/09_kofam_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)
        return True

    def parse_results(self):
        """Extract the significative KOs from the result of  `run_kofamscan()`
        """
        # Recover the complete list of KO
        result_d = dict()
        with open(self.ko_list, 'r') as fi:
            lines = fi.readlines()
            for line in lines:
                if line.startswith('knum'):
                    pass
                else:
                    result_d[line.split("\t")[0]] = 0
        # Read the results from KOfamScan
        with open(self.results, 'r') as fi:
            lines = fi.readlines()
            for line in lines:
                line = line.rstrip().split('\t')
                if line[0] == "*":
                    if line[2] in result_d.keys():
                        result_d[line[2]] = 1
                    else:
                        print("This KO (%s) is not present in %s" % (
                              line[2], self.ko_list)
                              )
        # Export the presence/absence table
        with open(self.results + '.matrix_MPE.tsv', 'w') as fo:
            print("KO\tsample", file=fo)
            for k, v in result_d.items():
                print(k, v, sep='\t', file=fo)
        return True


if __name__ == '__main__':
    test = KO_annot(project='damien/test_32', new_dir=False,
                    ko_files='damien/ko_fam')
    test.parse_results()
