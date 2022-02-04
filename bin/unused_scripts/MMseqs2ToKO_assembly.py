import re
import sys

file_name = sys.argv[1]

fi = open(file_name,"r")
for li in fi :
	li = li.rstrip()
	lu = li.split("\t")
	trini = lu[0]
	KEGG_Uniref = lu[1]
	kegg_uniref = KEGG_Uniref.split("_")
	KEGG = kegg_uniref[0]
	uniref = kegg_uniref[1]
	IDpour = float(lu[2])
	l_ali = lu[3]
	l_ali_re = re.search("\w+",l_ali)
	l_ali_a = l_ali_re.group(0)
	e_value = float(lu[10])
	bitscore = int(lu[11])
	
	print(trini + "\t" + KEGG)
	
	
fi.close()
