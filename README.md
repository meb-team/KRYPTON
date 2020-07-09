KRYPTON 

euKaRYote ProtisT fOnctionnal aNnotation of transcriptome 

KRYPTON est un pipeline permettant l'assemblage et l'annotation fonctionnelle de transcriptomes.


KRYPTON combine Trinity, mmseqs2 clust et mmseqs2 search et MetaPathExplorer

 schema du pipeline 


Il présente deux mode d'utilisation :

- mode "reads" :
Permet de faire l'assemblage et l'annotation fonctionnelle à partir de reads type illumina

- mode "assembly" :
Permet de faire l'annotation fonctionnelle à partir d'un assemblage déjà réalisé



INSTALLATION :

Dépendances :

python 3.5

Trinity v2.9.1

MMseqs2_v2018 



git clone https://github.com/meb-team/CRYPTON.git

cd KRYPTION


exemple d'utilisation :


-exemple mode "reads" :
python3.5 ./bin/CRYPTON.py /chemin/reads/forward.fastq.gz /chemin/reads/reverse.fastq.gz /chemin/output


-exemple mode  "assembly" :
python3.5 ./bin/CRYPTON.py /chemin/assemblage chemin/output

