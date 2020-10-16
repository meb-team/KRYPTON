# KRYPTON



[![Build Status](https://github.com/meb-team/CRYPTON.git)](https://github.com/meb-team/CRYPTON)

### euKaRYote ProtisT fOnctionnal aNnotation of transcriptome



KRYPTON est un pipeline permettant l'assemblage et l'annotation fonctionnelle de transcriptomes.

KRYPTON combine Trinity, mmseqs2 clust, mmseqs2 search et MetaPathExplorer

![Workflow Krypton](https://github.com/meb-team/KRYPTON/blob/master/Workflow_KRYPTON.PNG)

## DEPENDANCES :

  - python 3.5
  - fastQC v0.11.4
  - Trimmomatic v0.33
  - Trinity v2.9.1
  - MMseqs2_v2018

# INSTALLATION :

```sh
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
```

Il y'a trois modes d'utilisation de KRYPTON; soit avec des reads (mode="reads"), soit avec un assemblage déjà réalisé (mode="assembly"), soit avec un fichier contenant les cds (mode="cds").

### Exemple d'utilisation :

#### Important : 

. Tous les chemins utilisés (reads, assemblages, dossier output) doivent être des chemins absolus

. Le mode "reads" doit utiliser UNIQUEMENT des reads paired (reads forward et reads backward) 

 - exemple mode "reads" :

```sh
python3.5 ./bin/KRYPTON.py reads /chemin/absolu/reads/forward.fastq.gz /chemin/absolu/reads/reverse.fastq.gz /chemin/absolu/output
```
- exemple mode "assembly" : 
```sh
python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/assemblage chemin/absolu/output
```
- exemple mode "cds" : 
```sh
python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/fichier_cds chemin/absolu/output
```

### Résultats

Les séquences de la clusterisation nucléotidique se trouvent : 

```sh
/chemin/absolu/dossier_output/mmseqs2_Trans_clust/clusterRes_rep_seq.fasta
```

Les séquences protéiques se trouvent : 

```sh
/chemin/absolu/dossier_output/Transdecoder/clusterpep.fasta
```

Les séquences de la clusterisation protéique se trouvent : 

```sh
/chemin/absolu/dossier_output/mmseqs2_Pep_clust/clusterpepRes_rep_seq.fasta
```

Les résultats de l'annotation fonctionnelle se trouvent dans le dossier : 


```sh
/chemin/absolu/dossier_output/mmseqs2_out/results_out/
```

Le lien entre les Ko et les map se trouvent :

```sh
/chemin/absolu/dossier_output/mmseqs2_out/results_out/alignment_trinity_ko_map.tsv
```

Le lien entre les Ko et l'Orthologie de la séquence se trouvent :

```sh
/chemin/absolu/dossier_output/mmseqs2_out/results_out/alignment_trinity_ko_ortho.tsv
```

Le résultats de l'alignement de l'assemblage Trinity avec Uniref90 : 

```sh
/chemin/absolu/dossier_output/mmseqs2_out/results_out/alignment_trinity_Uniref90_sorted.tsv
```

Pour visualisé les résultats via MetaPathExplorer : 

```sh
/chemin/absolu/dossier_output/mmseqs2_out/results_out/MetaPAthExplorer/
```

### Jeu de données test 

Un jeu de donné test est fourni dans le dossier : File_test.
Ce jeu de donné provient du projet MMETSP ré-assemblé par L. Johnson _et al._, 2018 (https://academic.oup.com/gigascience/article/8/4/giy158/5241890) 
téléchargé sur : https://zenodo.org/record/1212585


