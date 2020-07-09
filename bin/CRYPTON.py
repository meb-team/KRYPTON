import os, re
import sys
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE

read_forward = sys.argv[1]
read_backward = sys.argv[2]
dir_output = sys.argv[3]
assembly_mode = "trinity"




def Creation_dossier(nom_dossier) :
	# creer le dossier si il n'existe pas
	if not os.path.exists(nom_dossier):
		os.makedirs(nom_dossier)
	# on se place dans le dossier
	os.chdir(nom_dossier)
	

def Check_etape(fichier_teste,commande) :
	# va verifier si une etape a deja ete realise ou non
	try :
		process = Popen(['ls {}'.format(fichier_teste)], stdout=PIPE, stderr=PIPE, shell=True)
		stdout, stderr = process.communicate()
		stdout = stdout.rstrip()
		stdout = stdout.decode("utf-8")	
		with open(stdout) :
			pass	
	except :
		os.system(commande)
		






################################################### main ###################################################


Creation_dossier(dir_output)


########################## Partie assemblage ##########################

##### fastqc #####



# définit un dossier de sortie pour fastqc
output_fastqc_raw = "fastqc_raw"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(output_fastqc_raw)


fichier_cible = "*1_1*.zip"
commande = "fastqc {} {} --outdir ./ --threads 20 > raw_fastqc.log 2>&1".format(read_forward,read_backward)

Check_etape(fichier_cible,commande)

print("etape fastq_raw terminee")



##### trimmomatic #####

# permet de revenir au dossier de resultats
os.chdir(dir_output)

# definit le dossier de sortie pour trimmomatic
output_trimmomatic = "trimmomatic_out"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(output_trimmomatic)

fichier_cible = "forward*.paired.fastq"
commande = "java -jar /usr/local/Trimmomatic-0.33/trimmomatic-0.33.jar PE -threads 20 {} {} forward.trimmomatic.paired.fastq forward.trimmomatic.unpaired.fastq reverse.trimmomatic.paired.fastq reverse.trimmomatic.unpaired.fastq MINLEN:32 SLIDINGWINDOW:10:20 LEADING:5 TRAILING:5 > trimmomatic.log 2>&1".format(read_forward,read_backward)

Check_etape(fichier_cible,commande)

print("etape trimmomatic terminee")

trim_forward = "forward.trimmomatic.paired.fastq"
trim_backward = "reverse.trimmomatic.paired.fastq"


path_trim_forward = os.path.abspath(trim_forward)
path_trim_backward = os.path.abspath(trim_backward)



##### trim_fastqc #####


# permet de revenir au dossier de resultats
os.chdir(dir_output)

# définit un dossier de sortie pour trim_fastqc
output_fastqc_trimmed = "fastqc_trimmed"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(output_fastqc_trimmed)

fichier_cible = "forward*.zip"
commande = "fastqc {} {} --outdir ./ --threads 20 > trim_fastqc.log 2>&1".format(path_trim_forward,path_trim_backward)

Check_etape(fichier_cible,commande)


print("etape trim_fastqc terminee")



if assembly_mode == "trinity" :

	##### Trinity #####


	# permet de revenir au dossier de resultats
	os.chdir(dir_output)

	# définit un dossier de sortie pour Trinity
	output_trinity = "trinity_out"

	# creer le dossier de sortie et s'y deplace dedans
	Creation_dossier(output_trinity)

	fichier_cible = "Trinity.fasta"
	commande = "Trinity --seqType fq --left {} --right {} --output ../trinity_out --CPU 20 --max_memory 100G > trinity.log 2>&1".format(path_trim_forward,path_trim_backward)
	
	Check_etape(fichier_cible,commande)
	
	
	print("etape assemblage terminee")
	
	
	file_trinity = "Trinity.fasta"
	
	# donne le chemin absolue du fichier file_trinity
	path_trinity = os.path.abspath(file_trinity)




########################## Clusterisation ##########################

# permet de revenir au dossier de resultats
os.chdir(dir_output)

output_clust = "mmseqs2_out_clust"

Creation_dossier(output_clust)

fichier_cible = "clusterRes_cluster.tsv"
commande = "mmseqs easy-linclust {} clusterRes tmp > cluster.log 2>&1".format(path_trinity)

Check_etape(fichier_cible,commande)

#os.system("mmseqs easy-linclust {} clusterRes tmp").format(path_trinity)

path_clust = os.path.abspath("clusterRes_rep_seq.fasta")

print("etape clusterisation terminee")
	
########################## Partie Annotation Fonnctionnelle ##########################



##### MMseqs2 #####

if assembly_mode == "trinity" :
	#path_assemblage = path_trinity
	path_assemblage = path_clust
	

# permet de revenir au dossier de resultats
os.chdir(dir_output)

# définit un dossier de sortie pour MMseqs2
output_mmseqs = "mmseqs2_out"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(output_mmseqs)



try :
		process = Popen(['ls *.tsv'], stdout=PIPE, stderr=PIPE, shell=True)
		stdout, stderr = process.communicate()
		stdout = stdout.rstrip()
		stdout = stdout.decode("utf-8")
		with open(stdout) :
			pass
except :
		
	# lance la commande pour indexer trinity pour l'utilisation de MMseqs2
	os.system("mmseqs createdb {} {}DB --dbtype 2 -v 1 > mmseqs2_{}DB.log 2>&1".format(path_assemblage,assembly_mode,assembly_mode))

	# lance la commande pour indexer Uniref90 pour l'utilisation de MMseqs2
	os.system("mmseqs createdb /databis/milisav/raw/FMAP/FMAP_data/orthology_uniref90_2_2157_4751.20190806012959.fasta ortho_Uniref90DB --dbtype 1 -v 1 > mmseqs2_Uniref90DB.log 2>&1")

	# lance la commande pour lancer MMseqs2 sur Uniref90 et Trinity / oases
	os.system("mmseqs search {}DB ortho_Uniref90DB alignment_{}_Orhto_Uniref90DB tmp -s 7.5 --max-seqs 1 -e 10e-5 --threads 20 -v 1 > alignement_{}_Orhto_Uniref90DB.log 2>&1".format(assembly_mode,assembly_mode,assembly_mode))

	# passage du format DB a format tsv pour les résultats
	os.system("mmseqs convertalis {}DB ortho_Uniref90DB alignment_{}_Orhto_Uniref90DB alignment_{}_Ortho_Uniref90.tsv --format-mode 2 -v 3".format(assembly_mode,assembly_mode,assembly_mode,assembly_mode))

	file_alignment = "alignment_{}_Ortho_Uniref90.tsv".format(assembly_mode)

	path_file_alignment = os.path.abspath(file_alignment)

		

print("etape mmseqs2 alignement terminee")




# définit le dossier des resultats
results_out = "results_out"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(results_out)

try :
		process = Popen(['ls *ortho.tsv'], stdout=PIPE, stderr=PIPE, shell=True)
		stdout, stderr = process.communicate()
		stdout = stdout.rstrip()
		stdout = stdout.decode("utf-8")
		with open(stdout) :
			pass
except :

	# tri du fichier de sortie de MMseqs2 sur la colonne le nom de la séquence et le bitscore dans l'ordre décroissant
	os.system("sort -rk 1,12 {} > alignment_{}_Uniref90_sorted.tsv".format(path_file_alignment,assembly_mode))

	# recuperation des meilleurs transcrits avec un coverage supérieur a 80%
	os.system("python3.5 /databis/milisav/bin/Annota_fonc/format_mmseqs.py alignment_{}_Uniref90_sorted.tsv 0 80 > alignment_{}_Ortho_Uniref90_sorted_filtred.tsv".format(assembly_mode,assembly_mode))

	# on recupere uniquement le trinity et le ko associe
	os.system("python3.5 /databis/milisav/bin/Annota_fonc/MMseqs2ToKO.py alignment_{}_Ortho_Uniref90_sorted_filtred.tsv > alignment_{}_ko.tsv".format(assembly_mode,assembly_mode))

	# on associe le transcrit et son ko a une orhtologie
	os.system("python3.5 /databis/milisav/bin/Annota_fonc/ko_To_Ortho.py alignment_{}_ko.tsv > alignment_{}_ko_ortho.tsv".format(assembly_mode,assembly_mode))

	# on associe un transcrit et son ko a une map et une voie metabolique
	os.system("python3.5 /databis/milisav/bin/Annota_fonc/ko_To_map.py alignment_{}_ko.tsv > alignment_{}_ko_map.tsv".format(assembly_mode,assembly_mode))
	
	# on compte le nombre de ko unique
	os.system("cut -f2 alignment_{}_ko_map.tsv | uniq -c > ko_list_count.txt".format(assembly_mode))
	
	# on echange les colonne 1 et 2
	os.system('''awk '{ print $2 "\t" $1 }' ko_list_count.txt > ko_matrix.tsv''')
	
	# on va creer un header au fichier precedent pour etre utiliser par MetaPathExplorer
	os.system("python3.5 /databis/milisav/bin/Annota_fonc/ajout_header.py ko_matrix.tsv > ko_matrix_header.tsv")
	
print("etape mmseqs2 anotation terminee")




##### MetaPathExplorer #####


fichier_cible = "$HOME/MetaPathExplorer3/bin/MetaPathExplorer"
commande = "git clone https://github.com/meb-team/MetaPathExplorer.git $HOME/MetaPathExplorer3"

Check_etape(fichier_cible,commande)

#lecture_file_ini = open("$HOME/MetaPathExplorer3/conf/MetaPathExplorer.ini","r")


os.system("cp /databis/milisav/MetaPathExplorer3/conf/MetaPathExplorer.ini /databis/milisav/MetaPathExplorer3/conf/MetaPathExplorer.init")

lecture_file_ini = open("/databis/milisav/MetaPathExplorer3/conf/MetaPathExplorer.ini","r")

ecriture_file_ini = open("/databis/milisav/MetaPathExplorer3/conf/MetaPathExplorer.init","w")

i = 0

for li in lecture_file_ini :
	
	i += 1
		
	if i == 27 :
		#ecriture_file_ini.write("outdir=./MetaPAthExplorer\n")
		if li.startswith("outdir=examples/MetaPathExplorer") :
				ecriture_file_ini.write('outdir=./MetaPAthExplorer')
	else :
		ecriture_file_ini.write(li)
		
ecriture_file_ini.close()

lecture_file_ini.close()


#os.system("perl $HOME/MetaPathExplorer3/bin/MetaPathExplorer --ini $HOME/MetaPathExplorer3/conf/MetaPathExplorer.init --input matrix $HOME/data/AK_bis/mmseqs2_out/results_out/ ko_matrix_header.tsv --force > MetaPAthExplorer.log 2>&1")

### quelle version utiliser ?

os.system("perl /data/share/MetaPathExplorer/MetaPathExplorer/bin/MetaPathExplorer --ini $HOME/MetaPathExplorer3/conf/MetaPathExplorer.init --input matrix $HOME/data/AK_bis/mmseqs2_out/results_out/ ko_matrix_header.tsv --force > MetaPAthExplorer.log 2>&1")

