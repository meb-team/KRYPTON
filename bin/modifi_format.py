from collections import defaultdict
import os, re
import sys


file_name = sys.argv[1]

dico_seq = defaultdict(str)

from pathlib import Path
 
directory = Path(__file__).parent

print(directory)


file_open = open(file_name,"r")

for li in file_open :
	li = li.rstrip()
	if li.startswith(">") :
		nom_seq = li 
	else :
		dico_seq[nom_seq] = dico_seq[nom_seq] + li

	
file_open.close()


for elem in dico_seq :
	print(elem)
	print(dico_seq[elem])
