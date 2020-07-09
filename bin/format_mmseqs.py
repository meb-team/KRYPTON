import sys
import re

### ce fichier permet de faire un selectionner les transcrits sur le meilleur bitscore avec un coverage >= a 80 

file_name = sys.argv[1]
identite = sys.argv[2]
filtre_coverage = sys.argv[3]

trini_base = ""
score_base = 0

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
	LQu = int(lu[12])
	LSu = int(lu[13]) 
	if LQu < LSu :
		Seq_Q_S_courte = LQu
	if LQu > LSu :
		Seq_Q_S_courte = LSu
	coverage =  (int(l_ali_a) /  Seq_Q_S_courte) * 100
	
	if trini != trini_base :
		score_base = 0
		trini_base = trini
		if bitscore > score_base :
			score_base = bitscore
			if coverage >= int(filtre_coverage) :
				if IDpour >= float(identite) :
					if coverage <= 120 :
						print(li)
			
	if trini == trini_base :
		if bitscore > score_base :
			score_base = bitscore
			if coverage >= int(filtre_coverage) :
				if IDpour >= float(identite) :
					if coverage <= 120 :
						print(li)
	

fi.close()
