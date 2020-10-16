# KRYPTON



[![Build Status](https://github.com/meb-team/CRYPTON.git)](https://github.com/meb-team/CRYPTON)

### euKaRYote ProtisT fOnctionnal aNnotation of transcriptome



KRYPTON est un pipeline permettant l'assemblage et l'annotation fonctionnelle de transcriptomes.

KRYPTON combine Trinity, mmseqs2 clust et mmseqs2 search et MetaPathExplorer

![Workflow Krypton](https://github.com/meb-team/KRYPTON/blob/master/Workflow_KRYPTON.PNG)

## DEPENDANCES :

  - python 3.5
  - Trinity v2.9.1
  - MMseqs2_v2018

# INSTALLATION :

```sh
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
```

Il y'a trois modes d'utilisation de KRYPTON; soit avec des reads (mode="reads"), soit avec un assemblage déjà réalisé (mode="assembly"), soit avec un fichier contenant les cds (mode="cds").

### Exemple d'utilisation :

#### Important : Tous les chemins utilisés (reads,assemblages,dossier output) doivent être des chemins absolus

 - exemple mode "reads" :

```sh
python3.5 ./bin/KRYPTON.py reads /chemin/absolu/reads/forward.fastq.gz /chemin/absolu/reads/reverse.fastq.gz /chemin/output
```
- exemple mode "assembly" : 
```sh
python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/assemblage chemin/absolu/output
```
- exemple mode "cds" : 
```sh
python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/fichier_cds chemin/absolu/output
```


