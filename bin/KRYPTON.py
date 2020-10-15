import os, re
import sys
import time
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE
from pathlib import Path

mode_pipeline = sys.argv[1]

if mode_pipeline == "reads" :
 
	read_forward = sys.argv[2]
	read_backward = sys.argv[3]
	dir_output = sys.argv[4]
	assembly_mode = "trinity"
	
if mode_pipeline == "assembly" or mode_pipeline == "cds" :
	assembly_input = sys.argv[2]
	dir_output = sys.argv[3]
	assembly_mode = "trinity"
	path_assembly_input = os.path.abspath(assembly_input)




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



print("Bienvenue sur le pipeline Krypton, la totalité des étapes risque de prendre du temps soyez patient." )

debut_time_Global = time.time()

directory_KRIPTON = Path(__file__).parent

Creation_dossier(dir_output)



if mode_pipeline == "reads" :

	########################## Partie assemblage ##########################

	##### fastqc #####

	print("Debut de l etape de fastqc sur les reads, cette etape peut prendre du temps, patience.")	
	
	debut_timefastqc_raw = time.time()

	# définit un dossier de sortie pour fastqc
	output_fastqc_raw = "fastqc_raw"

	# creer le dossier de sortie et s'y deplace dedans
	Creation_dossier(output_fastqc_raw)


	fichier_cible = "*1_1*.zip"
	commande = "fastqc {} {} --outdir ./ --threads 20 > raw_fastqc.log 2>&1".format(read_forward,read_backward)

	Check_etape(fichier_cible,commande)


	fin_timefastqc_raw = time.time()
	
	temps_fastqc_raw = fin_timefastqc_raw - debut_timefastqc_raw
	
	if temps_fastqc_raw > 60 :
		temps_fastqc_raw_min = temps_fastqc_raw / 60
		print("etape fastq_raw terminee, cette étape a pris "+ str(temps_fastqc_raw_min) +" min.")
	else :
		print("etape fastq_raw terminee, cette étape a pris "+ str(temps_fastqc_raw) +" sec.")


	##### trimmomatic #####
	
	print("Debut de l etape de nettoyage avec trimmomatic des reads, cette etape peut prendre du temps, patience.")	
	
	debut_timeTrim = time.time()

	# permet de revenir au dossier de resultats
	os.chdir(dir_output)

	# definit le dossier de sortie pour trimmomatic
	output_trimmomatic = "trimmomatic_out"

	# creer le dossier de sortie et s'y deplace dedans
	Creation_dossier(output_trimmomatic)

	fichier_cible = "forward*.paired.fastq"
	commande = "java -jar /usr/local/Trimmomatic-0.33/trimmomatic-0.33.jar PE -threads 20 {} {} forward.trimmomatic.paired.fastq forward.trimmomatic.unpaired.fastq reverse.trimmomatic.paired.fastq reverse.trimmomatic.unpaired.fastq MINLEN:32 SLIDINGWINDOW:10:20 LEADING:5 TRAILING:5 > trimmomatic.log 2>&1".format(read_forward,read_backward)

	Check_etape(fichier_cible,commande)


	fin_timeTrim = time.time()
	
	temps_Trim = fin_timeTrim - debut_timeTrim

	if temps_Trim > 60 :
		temps_Trim_min = temps_Trim / 60
		print("etape Trimmomatic terminee, cette étape a pris "+ str(temps_Trim_min) +" min.")
	else :
		print("etape Trimmomatic terminee, cette étape a pris "+ str(temps_Trim) +" sec.")


	trim_forward = "forward.trimmomatic.paired.fastq"
	trim_backward = "reverse.trimmomatic.paired.fastq"


	path_trim_forward = os.path.abspath(trim_forward)
	path_trim_backward = os.path.abspath(trim_backward)



	##### trim_fastqc #####


	print("Debut de l etape de fastqc sur les reads nettoye par Trimmomatic, cette etape peut prendre du temps, patience.")	
	
	debut_timefastqc_Trim = time.time()


	# permet de revenir au dossier de resultats
	os.chdir(dir_output)

	# définit un dossier de sortie pour trim_fastqc
	output_fastqc_trimmed = "fastqc_trimmed"

	# creer le dossier de sortie et s'y deplace dedans
	Creation_dossier(output_fastqc_trimmed)

	fichier_cible = "forward*.zip"
	commande = "fastqc {} {} --outdir ./ --threads 20 > trim_fastqc.log 2>&1".format(path_trim_forward,path_trim_backward)

	Check_etape(fichier_cible,commande)

	
	fin_timefastqc_Trim = time.time()
	
	temps_fastqc_Trim = fin_timefastqc_Trim - debut_timefastqc_Trim
	
	if temps_fastqc_Trim > 60 :
		temps_fastqc_Trim_min = temps_fastqc_Trim / 60
		print("etape trim_fastqc terminee, cette étape a pris "+ str(temps_fastqc_Trim_min) +" min.")
	else :
		print("etape trim_fastqc terminee, cette étape a pris "+ str(temps_fastqc_Trim) +" sec.")
	
	

	if assembly_mode == "trinity" :

		##### Trinity #####
	
		print("Debut de l etape d'assemblage sur les reads nettoye par Trimmomatic, cette etape est longue, patience !!!")	
	
		debut_timeTrinity = time.time()
				
		

		# permet de revenir au dossier de resultats
		os.chdir(dir_output)

		# définit un dossier de sortie pour Trinity
		output_trinity = "trinity_out"

		# creer le dossier de sortie et s'y deplace dedans
		Creation_dossier(output_trinity)

		fichier_cible = "Trinity.fasta"
		commande = "Trinity --seqType fq --left {} --right {} --output ../trinity_out --CPU 20 --max_memory 100G > trinity.log 2>&1".format(path_trim_forward,path_trim_backward)
	
		Check_etape(fichier_cible,commande)
		
		
		fin_timeTrinity = time.time()
	
		temps_Trinity = fin_timeTrinity - debut_timeTrinity
	
		temps_Trinity_min = temps_Trinity / 60
		print("etape assemblage Trinity terminee, cette étape a pris "+ str(temps_Trinity_min) +" min.")
		
	
		file_trinity = "Trinity.fasta"
	
		# donne le chemin absolue du fichier file_trinity
		path_trinity = os.path.abspath(file_trinity)


if mode_pipeline == "assembly" or mode_pipeline == "cds" :
	os.system("python3.5 {}/modifi_format.py {} > assembly.fasta".format(directory_KRIPTON,assembly_input))
	path_assembly_modif = os.path.abspath("assembly.fasta")
	path_trinity = path_assembly_modif


if mode_pipeline == "assembly" or mode_pipeline == "reads" :

	########################## Clusterisation ##########################

	# permet de revenir au dossier de resultats
	os.chdir(dir_output)

	output_clust = "mmseqs2_Trans_clust"

	Creation_dossier(output_clust)

	fichier_cible = "clusterRes_cluster.tsv"
	commande = "mmseqs easy-linclust {} clusterRes tmp > cluster.log 2>&1".format(path_trinity)

	Check_etape(fichier_cible,commande)


	path_clust = os.path.abspath("clusterRes_rep_seq.fasta")

	print("etape clusterisation terminee")
	
	
	
##########################	Transdecoder	##########################

# permet de revenir au dossier de resultats
os.chdir(dir_output)

print("Debut de l etape de traduction des transcrits apres une clusterisation en prteines, cette etape peut prendre du temps, patience.")	
	
debut_timeTansdecoder = time.time()



output_transdecoder = "Transdecoder"

Creation_dossier(output_transdecoder)

if mode_pipeline == "assembly" or mode_pipeline == "reads" :

	os.system("TransDecoder.LongOrfs -m 30 -t {}".format(path_clust))

	os.system("TransDecoder.Predict -t {}".format(path_clust))

	os.system("python3.5 {}/modifi_format.py clusterRes_rep_seq.fasta.transdecoder.pep > clusterpep.fasta 2>&1".format(directory_KRIPTON))

if mode_pipeline == "cds" :

	os.system("TransDecoder.LongOrfs -m 30 -t {} 2>&1".format(path_trinity))

	os.system("TransDecoder.Predict -t {} 2>&1".format(path_trinity))

	os.system("python3.5 {}/modifi_format.py assembly.fasta.transdecoder.pep > clusterpep.fasta 2>&1".format(directory_KRIPTON))



fin_timeTansdecoder = time.time()
	
temps_Tansdecoder = fin_timeTansdecoder - debut_timeTansdecoder
	
temps_Tansdecoder_min = temps_Tansdecoder / 60

print("etape Transdecoder terminee, cette étape a pris "+ str(temps_Tansdecoder_min) +" min.")




##########################	2 eme clusterisation sur les proteines ##########################


# permet de revenir au dossier de resultats
os.chdir(dir_output)

output_Pep_clust = "mmseqs2_Pep_clust"

Creation_dossier(output_Pep_clust)


os.system("mmseqs easy-linclust ../Transdecoder/clusterpep.fasta clusterpepRes tmp > cluster.log 2>&1")

path_clust_2 = os.path.abspath("clusterpepRes_rep_seq.fasta")

print("etape 2 eme clusterisation terminee")




	

########################## Partie Annotation Fonnctionnelle ##########################

#path_clust_2 = "/databis/milisav/data/MMETSP1161/NCGR/mmseqs2_Pep_clust/clusterpepRes_rep_seq.fasta"

##### MMseqs2 #####
if mode_pipeline == "assembly" :
	if assembly_mode == "trinity" :
		path_assemblage = path_clust_2

if mode_pipeline == "reads" :
	if assembly_mode == "trinity" :
		path_assemblage = path_clust_2


if mode_pipeline == "cds" :
	if assembly_mode == "trinity" :
		path_assemblage = path_clust_2

# permet de revenir au dossier de resultats
os.chdir(dir_output)

# définit un dossier de sortie pour MMseqs2
output_mmseqs = "mmseqs2_out"

# creer le dossier de sortie et s'y deplace dedans
Creation_dossier(output_mmseqs)


print("Debut de l etape d'alignement des proteines sur Uniref90, cette etape peut prendre du temps, patience.")	
	
debut_timeSearch = time.time()



try :
		process = Popen(['ls *.tsv'], stdout=PIPE, stderr=PIPE, shell=True)
		stdout, stderr = process.communicate()
		stdout = stdout.rstrip()
		stdout = stdout.decode("utf-8")
		with open(stdout) :
			pass
except :
		
	# lance la commande pour indexer trinity pour l'utilisation de MMseqs2
	os.system("mmseqs createdb {} {}DB --dbtype 1 -v 1 > mmseqs2_{}DB.log 2>&1".format(path_assemblage,assembly_mode,assembly_mode))

	# lance la commande pour indexer Uniref90 pour l'utilisation de MMseqs2
	os.system("mmseqs createdb /databis/milisav/raw/FMAP/FMAP_data/orthology_uniref90_2_2157_4751.20190806012959.fasta ortho_Uniref90DB --dbtype 1 -v 1 > mmseqs2_Uniref90DB.log 2>&1")

	# lance la commande pour lancer MMseqs2 sur Uniref90 et Trinity
	os.system("mmseqs search {}DB ortho_Uniref90DB alignment_{}_Orhto_Uniref90DB tmp -s 7.5 --max-seqs 1 -e 10e-5 --threads 20 -v 1 > alignement_{}_Orhto_Uniref90DB.log 2>&1".format(assembly_mode,assembly_mode,assembly_mode))

	# passage du format DB a format tsv pour les résultats
	os.system("mmseqs convertalis {}DB ortho_Uniref90DB alignment_{}_Orhto_Uniref90DB alignment_{}_Ortho_Uniref90.tsv --format-mode 2 -v 3".format(assembly_mode,assembly_mode,assembly_mode,assembly_mode))

	file_alignment = "alignment_{}_Ortho_Uniref90.tsv".format(assembly_mode)

	path_file_alignment = os.path.abspath(file_alignment)

	
	
fin_timeSearch = time.time()
	
temps_Search = fin_timeSearch - debut_timeSearch
	
temps_Search_min = temps_Search / 60

print("etape MMseqs2 terminee, cette étape a pris "+ str(temps_Search_min) +" min.")	





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
	os.system("python3.5 {}/format_mmseqs.py alignment_{}_Uniref90_sorted.tsv 0 80 > alignment_{}_Ortho_Uniref90_sorted_filtred.tsv".format(directory_KRIPTON,assembly_mode,assembly_mode))

	if mode_pipeline == "reads" :
	
		# on recupere uniquement le trinity et le ko associe
		os.system("python3.5 {}/MMseqs2ToKO.py alignment_{}_Ortho_Uniref90_sorted_filtred.tsv > alignment_{}_ko.tsv".format(directory_KRIPTON,assembly_mode,assembly_mode))
	
	if mode_pipeline == "assembly" or mode_pipeline == "cds" :
		# on recupere uniquement le trinity et le ko associe
		os.system("python3.5 {}/MMseqs2ToKO_assembly.py alignment_{}_Ortho_Uniref90_sorted_filtred.tsv > alignment_{}_ko.tsv".format(directory_KRIPTON,assembly_mode,assembly_mode))
	
	# on associe le transcrit et son ko a une orhtologie
	os.system("python3.5 {}/ko_To_Ortho.py alignment_{}_ko.tsv > alignment_{}_ko_ortho.tsv".format(directory_KRIPTON,assembly_mode,assembly_mode))

	# on associe un transcrit et son ko a une map et une voie metabolique
	os.system("python3.5 {}/ko_To_map.py alignment_{}_ko.tsv > alignment_{}_ko_map.tsv".format(directory_KRIPTON,assembly_mode,assembly_mode))
	
	# on compte le nombre de ko unique
	os.system("cut -f2 alignment_{}_ko_map.tsv | uniq -c > ko_list_count.txt".format(assembly_mode))
	
	# on echange les colonne 1 et 2
	os.system('''awk '{ print $2 "\t" $1 }' ko_list_count.txt > ko_matrix.tsv''')
	
	# on va creer un header au fichier precedent pour etre utiliser par MetaPathExplorer
	os.system("python3.5 {}/ajout_header.py ko_matrix.tsv > ko_matrix_header.tsv".format(directory_KRIPTON))
	
print("etape mmseqs2 anotation terminee")




##### MetaPathExplorer #####

path_results_out = os.path.abspath(results_out)



fichier_cible = "{}/MetaPathExplorer/bin/MetaPathExplorer".format(directory_KRIPTON)
commande = "git clone https://github.com/meb-team/MetaPathExplorer.git {}/MetaPathExplorer".format(directory_KRIPTON)

Check_etape(fichier_cible,commande)


os.system("cp {}/MetaPathExplorer/conf/MetaPathExplorer.ini {}/MetaPathExplorer/conf/MetaPathExplorer.init".format(directory_KRIPTON,directory_KRIPTON))


#lecture_file_ini = open("{}/MetaPathExplorer/conf/MetaPathExplorer.ini".format(directory_KRIPTON),"r")
test_file = "{}/MetaPathExplorer/conf/MetaPathExplorer.ini".format(directory_KRIPTON)
lecture_file_ini = open(test_file,"r")

ecriture_file_ini = open("{}/MetaPathExplorer/conf/MetaPathExplorer.init".format(directory_KRIPTON),"w")

i = 0

for li in lecture_file_ini :
	
	i += 1
		
	if i == 27 :
		if li.startswith("outdir=examples/MetaPathExplorer") :
				ecriture_file_ini.write('outdir=./MetaPAthExplorer')
	else :
		ecriture_file_ini.write(li)
		
ecriture_file_ini.close()

lecture_file_ini.close()



os.system("perl {}/MetaPathExplorer/bin/MetaPathExplorer --ini {}/MetaPathExplorer/conf/MetaPathExplorer.init --input matrix ./ ko_matrix_header.tsv --force > MetaPAthExplorer.log 2>&1".format(directory_KRIPTON,directory_KRIPTON))

#os.system("perl {}/../binaries/MetaPathExplorer/bin/MetaPathExplorer --ini {}/../binaries/MetaPathExplorer/conf/MetaPathExplorer.ini --input matrix ./ ko_matrix_header.tsv --force > MetaPAthExplorer.log 2>&1".format(directory_KRIPTON,directory_KRIPTON))

### quelle version utiliser ?

#os.system("perl /data/share/MetaPathExplorer/MetaPathExplorer/bin/MetaPathExplorer --ini {}/MetaPathExplorer/conf/MetaPathExplorer.init --input matrix {} ko_matrix_header.tsv --force > MetaPAthExplorer.log 2>&1".format(directory_KRIPTON,path_results_out))





fin_time_Global = time.time()
	
temps_Global = fin_time_Global - debut_time_Global
	
temps_Global_min = temps_Global / 60
temps_Global_H = temps_Global_min / 60
print("Krypton est terminee, il a ete realise en "+ str(temps_Global_H) +" heures.")
