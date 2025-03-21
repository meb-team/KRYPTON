# -*- coding: utf-8

import shutil
import krypton.utils as u


class MPE():
    def __init__(self, project=None, bin=None):
        self.project = project
        self.output = self.project + "/" + '10_MetaPathExplorer'
        self.matrix = self.project + "/09_ko_annot/" + \
                                     "09_kofam_results.tsv.matrix_MPE.tsv"
        self.bin = bin + '/bin/MetaPathExplorer'
        self.ini = self.project + '/10_MetaPathExplorer.ini'
        self._generate_ini_file()

    def _generate_ini_file(self):
        """change the outdir in the MPE init file"""
        with open(self.bin + '/conf/MetaPathExplorer.ini', 'r') as fi:
            with open(self.ini, 'w') as fo:
                lines = fi.readlines()
                for line in lines:
                    if line.startswith('outdir='):
                        fo.write(f"outdir={self.output}")
                    else:
                        fo.write(line)
        return True

    def run_MPE(self, step=None):
        command = f"perl {self.bin}/bin/MetaPathExplorer --ini {self.ini} " +\
                  f"--input matrix {self.matrix}"
        with open(f"{self.project}/10_MPE_logs.log", "w") as log:
            u.run_command(command, log=log, step=step)

        shutil.move(src=self.project + '/10_MPE_logs.log',
                    dst=self.output + '/10_MPE_logs.log')
        return True


if __name__ == '__main__':
    mpe = MPE(project='damien/test_42',
              bin='/home/dacourti/Documents/projects/MEB/KRYPTON')
    mpe.run_MPE(step='Test MetaPathExplorer')
