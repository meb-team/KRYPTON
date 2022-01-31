# -*- coding: utf-8

class KO_annot():
    def __init__(self, threads=None, project=None):
        self.max_threads = threads
        self.output = project + "/" + '09_ko_annot'
