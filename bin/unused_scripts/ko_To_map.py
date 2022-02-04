import os
import re
import sys

### ce programme permet de passer de trouver la voie metabolique a partir du ko

file_name = sys.argv[1]

dico_ko_map = {}
dico_map_pathway = {}


fi = open("/data/share/MetaPathExplorer/MetaPathExplorer/data/KEGG_orthology2pathway.tsv","r")
for li in fi :
	li = li.rstrip()
	li = li.split("\t")
	ko = li[0]
	map_ortho = li[1]
	dico_ko_map[ko] = map_ortho
	
fi.close()
	

fo = open("/data/share/MetaPathExplorer/MetaPathExplorer/data/KEGG_pathway.txt","r")
for lo in fo :
	lo = lo.rstrip()
	lo = lo.split("\t")
	maped = lo[0]
	pathway = lo[1]
	dico_map_pathway[maped] = pathway


fo.close()

	
	
fu = open(file_name,"r")
for lu in fu :
	lu = lu.rstrip()
	lu = lu.split("\t")
	trini = lu[0]
	ko = lu[1]
	if ko in dico_ko_map :
		print(trini + "\t" + ko + "\t" + dico_ko_map[ko] + "\t" + dico_map_pathway[dico_ko_map[ko]])
	
	
fu.close()
