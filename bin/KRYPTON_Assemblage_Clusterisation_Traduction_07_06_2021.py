import os, re
import sys
import time
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE
from pathlib import Path


"""
Damien
Tasks to do:
    - [ ] Use the module argparse for the parameters

    - [ ] use "with open(xxx, ?) as yyy" to read files. It is much more efficient
__authors__ = ['bmilisavljevic', 'AnthonyAUCLAIR', 'd-courtine']

import argparse

parser = argparse.ArgumentParser(description='Run KRYPTON') #setup the parser
parser.add_argument('--bucketin', help='Name of the bucket used to read data from', required=True)
parser.add_argument('--bucketout', help='Name of the bucket used to store data in', required=True)
parser.add_argument(['--mode', '-m'], help='Mode for the pipeline, between "reads", "assembly" and "cds".'
    default = "reads", choices = ['reads', 'assembly', 'cds'])
- outdir
- input data --> depend on the mode

"""

# On active un environnement conda avec python3.5 installe prealablement
#os.system("PATHCONDA=$(conda info | grep -i 'base environment' | awk -F" " '{print $4}')")
#os.system("source $PATHCONDA'/etc/profile.d/conda.sh'")
#os.system("conda activate snakes")
#os.system("source activate snakes")

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

"""
from initialize.py import nom_base_donnees_reference
from initialize.py import base_donnees_reference

annotation_Pfam = sys.argv[5]

if annotation_Pfam == "Pfam" :
        from initialize.py import base_reference_Pfam

if len(sys.argv) = 6 :
        nom_base_donnees_reference = sys.argv[5]
        base_donnees_reference = sys.argv[6]

if len(sys.argv) = 7 :
        nom_base_donnees_reference = sys.argv[6]
        base_donnees_reference = sys.argv[7]
"""

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
directory_KRYPTON = Path(__file__).parent
Creation_dossier(dir_output)

if mode_pipeline == "reads" :
        ########################## Partie assemblage ##########################
        ##### fastqc #####
        """
        Integrate this step into a function as it is used twice. Also make sure to control all
        parameters for fastqc, like the number of CPUs.
        """
        print("Debut de l etape de fastqc sur les reads, cette etape peut prendre du temps, patience.")
        debut_timefastqc_raw = time.time()
        # définit un dossier de sortie pour fastqc
        output_fastqc_raw = "fastqc_raw"
        # creer le dossier de sortie et s'y deplace dedans
        Creation_dossier(output_fastqc_raw)
        fichier_cible = "*1_1*.zip"
        commande = "fastqc {} {} --outdir ./ --threads 15 > raw_fastqc.log 2>&1".format(read_forward,read_backward)
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
        commande = "java -jar /opt/apps/trimmomatic-0.33/trimmomatic-0.33.jar PE {} {} forward.trimmomatic.paired.fastq forward.trimmomatic.unpaired.fastq reverse.trimmomatic.paired.fastq reverse.trimmomatic.unpaired.fastq MINLEN:32 SLIDINGWINDOW:10:20 LEADING:5 TRAILING:5 > trimmomatic.log 2>&1".format(read_forward,read_backward)

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
        print("Debut de l etape de fastqc sur les reads nettoyes par Trimmomatic, cette etape peut prendre du temps, patience.")
        debut_timefastqc_Trim = time.time()

        # permet de revenir au dossier de resultats
        os.chdir(dir_output)
        # définit un dossier de sortie pour trim_fastqc
        output_fastqc_trimmed = "fastqc_trimmed"

        # creer le dossier de sortie et s'y deplace dedans
        Creation_dossier(output_fastqc_trimmed)
        fichier_cible = "forward*.zip"
        commande = "fastqc {} {} --outdir ./ --threads 15 > trim_fastqc.log 2>&1".format(path_trim_forward,path_trim_backward)

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
                print("Debut de l etape d'assemblage sur les reads nettoyes par Trimmomatic, cette etape est longue, patience !!!")
                debut_timeTrinity = time.time()
                # permet de revenir au dossier de resultats
                os.chdir(dir_output)
                # définit un dossier de sortie pour Trinity
                output_trinity = "trinity_out"

                # creer le dossier de sortie et s'y deplace dedans
                Creation_dossier(output_trinity)

                fichier_cible "MMseqs2ToKO" = "Trinity.fasta"
                commande = "Trinity --seqType fq --left {} --right {} --output ../trinity_out --CPU 20 --max_memory 95G > trinity.log 2>&1".format(path_trim_forward,path_trim_backward)
                Check_etape(fichier_cible,commande)
                fin_timeTrinity = time.time()
                temps_Trinity = fin_timeTrinity - debut_timeTrinity
                temps_Trinity_min = temps_Trinity / 60
                print("etape assemblage Trinity terminee, cette étape a pris "+ str(temps_Trinity_min) +" min.")
                file_trinity = "Trinity.fasta"

                # donne le chemin absolue du fichier file_trinity
                path_trinity = os.path.abspath(file_trinity)

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

##########################      Transdecoder    ##########################

# permet de revenir au dossier de resultats
os.chdir(dir_output)
print("Debut de l etape de traduction des transcrits apres une clusterisation en proteines, cette etape peut prendre du temps, patience.")
debut_timeTansdecoder = time.time()

output_transdecoder = "Transdecoder"
Creation_dossier(output_transdecoder)
if mode_pipeline == "assembly" or mode_pipeline == "reads" :
        os.system("TransDecoder.LongOrfs -m 30 -t {}".format(path_clust))
        os.system("TransDecoder.Predict -t {}".format(path_clust))
        os.system("python {}/modifi_format.py clusterRes_rep_seq.fasta.transdecoder.pep > clusterpep.fasta 2>&1".format(directory_KRYPTON))

if mode_pipeline == "cds" :
        os.system("TransDecoder.LongOrfs -m 30 -t {} 2>&1".format(path_trinity))
        os.system("TransDecoder.Predict -t {} 2>&1".format(path_trinity))
        os.system("python {}/modifi_format.py assembly.fasta.transdecoder.pep > clusterpep.fasta 2>&1".format(directory_KRYPTON))

fin_timeTansdecoder = time.time()
temps_Tansdecoder = fin_timeTansdecoder - debut_timeTansdecoder
temps_Tansdecoder_min = temps_Tansdecoder / 60
print("etape Transdecoder terminee, cette étape a pris "+ str(temps_Tansdecoder_min) +" min.")
