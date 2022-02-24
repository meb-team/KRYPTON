#!/usr/bin/env python3
# -*- coding: utf-8

import sys
import time
import argparse
import krypton.utils as u


class KO_annot():
    def __init__(self, project=None, ko_list=None, data_path=None):
        self.output = project + "/" + '09_ko_annot'
        self.ko_list = ko_list
        self.results = self.output + '/09_kofam_results.tsv'

        # To output the results in txt files
        self.K0_name = data_path + '/KEGG_K0.tsv'
        self.K0_to_pathway = data_path + '/KEGG_K0_to_pathway.tsv'
        self.pathway_name = data_path + '/KEGG_pathways.tsv'

    def parse_results_for_MPE(self):
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

    def parse_results_as_txt(self):
        """
        1. Get the K0 <=> pathway relations from a file
        2. Read the K0famScan results
        3. export result in new dir with
            3.1 a summary file
            3.1 a file per map + mislaneous K0
        """

        # 1. get the pathway<=>K0 relations and pathway name
        P2K_d = dict()  # Key = map; value = list of K0s
        if u.is_file_exists(self.K0_to_pathway):
            with open(self.K0_to_pathway, 'r') as fi:
                lines = fi.readlines()
                for line in lines:
                    K0 = line.split('\t')[0].rstrip()
                    pathway = line.split('\t')[1].rstrip()
                    if pathway not in P2K_d.keys():
                        P2K_d[pathway] = [K0]
                    else:
                        P2K_d[pathway] += [K0]
        else:
            print(f"KRYPTON can't file the file {self.K0_to_pathway}.\n"
                  "Have you ran the script `bin/download_KEGG_data.py` during"
                  " the installation? If no, you can do it now and run:\n\t"
                  "<WIP> sorry... but it is possible to re-run KRYPTON in cds"
                  " mode.")
            sys.exit(1)

        pathway_name = dict()
        if u.is_file_exists(self.pathway_name):
            with open(self.pathway_name, 'r') as fi:
                lines = fi.readlines()
                for line in lines:
                    pathway = line.split('\t')[0].rstrip()
                    descrip = line.split('\t')[1].rstrip()
                    pathway_name[pathway] = descrip
        else:
            print(f"KRYPTON can't file the file {self.pathway_name}.\n"
                  "<WIP> sorry...")
            sys.exit(1)

        # 2. Read the KOfamscan results
        signif_res = dict()
        with open(self.results, 'r') as fi:
            lines = fi.readlines()
            for line in lines:
                line = line.rstrip().split('\t')
                if line[0] == "*":
                    if line[2] not in signif_res.keys():
                        signif_res[line[2]] = 0  # Tracking system
        signif_res_key_list = signif_res.keys()  # Get the list of K0s found

        # 3. write results
        # 3.1 map by map
        summary = dict()
        outdir = self.output + '/results_by_map'
        u.create_dir(outdir)
        # For all K0s of a map, are they present in the curent results?
        for map, K0_list in P2K_d.items():
            found = 0
            with open(f"{outdir}/{map}.txt", "w") as fo:
                for elem in K0_list:
                    if elem in signif_res_key_list:  # current K0 in our result?
                        signif_res[elem] += 1  # Tracking system
                        found += 1
                        print(elem, file=fo)
            # For the summary file
            summary[map] = [len(K0_list), found]  # nb total, #nb found

        # ## Track K0s not in maps, thanks tot he tracking system
        K0_not_in_pathway = list()
        for k, v in signif_res.items():
            if v == 0:
                K0_not_in_pathway.append(k)
        if len(K0_not_in_pathway) > 0:
            K0_not_in_pathway = list(set(K0_not_in_pathway))
            summary['mislanaeous'] = ['NA', len(K0_not_in_pathway)]
            with open(f"{outdir}/mislaneous_K0s.txt", 'w') as fo:
                [fo.write(f"{elem}\n") for elem in K0_not_in_pathway]

        # 3.2 Write the summary
        with open(f"{self.output}/results_summary.txt", 'w') as fo:
            print("pathway_id", "pathway_name", "K0_nb_total", "K0_nb_present",
                  "ratio", file=fo, sep='\t')
            for k, v in summary.items():
                if v[0] == 'NA':
                    print(k, k, v[0], v[1], v[0], file=fo, sep='\t')
                else:
                    print(k, pathway_name[k], v[0], v[1],
                          f"{int(v[1])/int(v[0]):.2f}", file=fo, sep='\t')
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse KoFamScan results",
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--project', help='Name of the project that was passed'
                        "to KRYPTON's main script.", metavar='', required=True)
    parser.add_argument('--files', help='Path to the directory containing '
                        'files "KEGG_K0_to_pathway.tsv", "KEGG_K0.tsv" and '
                        '"KEGG_pathways.tsv"', metavar="", required=True)
    parser.add_argument('--ko_list', help='Path to the file "ko_list"',
                        metavar="", required=True)
    args = parser.parse_args()

    time_global = [time.time()]
    analysis = KO_annot(project=args.project.rstrip('/'),
                        data_path=args.files.rstrip('/'),
                        ko_list=args.ko_list)
    analysis.parse_results_as_txt()
    analysis.parse_results_for_MPE()

    time_global.append(time.time())
    u.time_used(time_global, step="Parse K0FamScan results")
