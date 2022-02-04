import os, re
import sys

#### ce programme permet de mettre un head au fichier ko_list

file = sys.argv[1]

print("KO\tHeader")

file_open = open(file,"r")
for li in file_open :
	li = li.rstrip()
	print(li)
file_open.close()
