# KRYPTON



[![Build Status](https://github.com/meb-team/CRYPTON.git)](https://github.com/meb-team/CRYPTON)

### euKaRYote ProtisT fOnctionnal aNnotation of transcriptome

![Workflow Krypton](/Diapo workflow Krypton.jpg )

KRYPTON est un pipeline permettant l'assemblage et l'annotation fonctionnelle de transcriptomes.

KRYPTON combine Trinity, mmseqs2 clust et mmseqs2 search et MetaPathExplorer

## DEPENDANCES :

  - python 3.5
  - Trinity v2.9.1
  - MMseqs2_v2018

# INSTALLATION :

```sh
git clone https://github.com/meb-team/CRYPTON.git
cd KRYPTION
```

### Exemple d'utilisation :

 - exemple mode "reads" :

```sh
python3.5 ./bin/CRYPTON.py /chemin/reads/forward.fastq.gz /chemin/reads/reverse.fastq.gz /chemin/output
```
- exemple mode "assembly" : 
```sh
python3.5 ./bin/CRYPTON.py /chemin/assemblage chemin/output
```



