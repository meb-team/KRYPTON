#!/usr/bin/env python3
# -*- coding: utf-8

import os
import requests
import time
import krypton.utils as u

"""
The code present in this script is heavily inspired by a Nolwen's blog
post from bioinfo-fr.net!

https://bioinfo-fr.net/jouer-lapi-de-kegg

The KEGG API: https://www.kegg.jp/kegg/rest/keggapi.html
Links that will be used in this script
    - http://rest.kegg.jp/list/pathway ==> all maps and their name
    - http://rest.kegg.jp/list/ko ==> all K0 and their name
    - http://rest.kegg.jp/link/pathway/ko ==> K0 to map and ko
"""

pathways = "http://rest.kegg.jp/list/pathway"
K0 = "http://rest.kegg.jp/list/ko"
pathways_to_K0 = "http://rest.kegg.jp/link/pathway/ko"

# # Setup the output directory
out = os.path.dirname(os.path.abspath(__name__)) + '/ressources/KEGG_data/'

print("File will be downloaded in %s " % out)
try:
    u.check_dir_exists(out)
except Exception:
    u.create_dir(out)

# # Download the data
# ## Pathways
r = requests.get(pathways)
r_out = out + 'KEGG_pathways.tsv'
print(f"Download the list of pathways from KEGG in {r_out}")
with open(r_out, "w") as fo:
    lines = r.text.splitlines()
    for line in lines:
        """
        From "path:map00010	Glycolysis / Gluconeogenesis", get two items:
            - name: map00010
            - fct: Glycolysis / Gluconeogenesis
        """
        name = line.split("\t")[0].split(":")[1]
        fct = line.split("\t")[1]
        print(name, fct, sep="\t", file=fo)

time.sleep(2)  # wait 2 seconds

# ## K0s
s = requests.get(K0)
s_out = out + 'KEGG_K0.tsv'
print(f"Download the list of K0s from KEGG in {s_out}")
with open(s_out, "w") as fo:
    lines = s.text.splitlines()
    for line in lines:
        name = line.split("\t")[0].split(":")[1]
        fct = line.split("\t")[1]
        print(name, fct, sep="\t", file=fo)

time.sleep(2)

# ## Get the link between pathway and K0
t = requests.get(pathways_to_K0)
t_out = out + 'KEGG_K0_to_pathway.tsv'
print(f"Download the links between pathways and K0s from KEGG in {t_out}")
with open(t_out, "w") as fo:
    lines = t.text.splitlines()
    for line in lines:
        ko = line.split("\t")[0].split(":")[1]
        pathway = line.split("\t")[1].split(":")[1]
        if pathway.startswith("map"):
            print(ko, pathway, sep="\t", file=fo)

print("All data were downloaded from KEGG.")
