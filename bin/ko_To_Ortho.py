import os
import re
import sys

### ce programme permet de trouver le l'orthologie à partir  du KO

file_name = sys.argv[1]

dico_ko_ortho = {}



fi = open("/data/share/MetaPathExplorer/MetaPathExplorer/data/KEGG_orthology.txt","r")
for li in fi :
	li = li.rstrip()
	li = li.split("\t")
	ko_KEGG = li[0]
	prot = li[1]
	
	int_KEGG = ko_KEGG.split(":")
	KEGG = int_KEGG[1]
	dico_ko_ortho[KEGG] = prot
	
	
fi.close()




fu = open(file_name,"r")
for lu in fu :
	lu = lu.rstrip()
	lu = lu.split("\t")
	trini = lu[0]
	ko = lu[1]
	if ko in dico_ko_ortho :
		print(trini + "\t" + ko + "\t" + dico_ko_ortho[ko])
	
	
fu.close()
