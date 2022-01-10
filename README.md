# KRYPTON

[![Build Status](https://github.com/meb-team/CRYPTON.git)](https://github.com/meb-team/CRYPTON)

## Introduction

This package, _euKaRYote ProtisT fOnctionnal aNnotation of transcriptome_,
abbreviated as _KRYPTON_, is a Python package containing a pipeline for
transcriptome assembly and annotation (functional and taxonomic).  
KRYPTON combines Trinity, MMseqs2 _clust_, MMseqs2 _search_ and MetaPathExplorer.

![Workflow KRYPTON](ressources/Workflow_KRYPTON.PNG)

## To-do list:

- [ ] check if a step ended nicely?
    - [ ] trimmomatic output the information in STDOUT/STDERR
        (_TrimmomaticPE: Completed successfully_)
    - [ ] Trinity too ("_All commands completed successfully. :-)_")
- [ ] Add parameters to tweak tool parameters:
    - [ ] fastQC _--threads_
    - [ ] trimmomatic _MINLEN:32 SLIDINGWINDOW:10:20 LEADING:5 TRAILING:5_
    - [ ] trinity _--CPU_ and _--max_memory_
    - [ ] MMseqs2 _WIP_

## Dependencies

  - python >= 3.5
  - numpy >= 1.22
  - fastQC >= 0.11.4
  - Trimmomatic >= 0.33
  - Trinity >= v 2.9.1
  - MMseqs2 v 10-6d92c

## Install

```sh
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
pip install -e .
```

## Usage

There are kind of usage. From the sequencing _reads_ (`--mode reads`), or by
providing a set of transcripts (`--mode assembly`) or from a set of CDS (`--mode cds`).

The help menu is available with the command `python bin/KRYPTON.py -h`, and bellow.

```text
usage: KRYPTON.py [-h] [--mode {reads,assembly,cds}] --out OUT_DIR
                  [--overwrite] [--single-end] [--r1] [--r2] [--trimmomatic]
                  [--transcripts] [--cds] [--bucketin BUCKET_IN]
                  [--bucketout BUCKET_OUT] [--run-on-HPC]

Run the pipeline KRYPTON, for transcriptome assembly and annotation

optional arguments:
  -h, --help            show this help message and exit

Mandatory arguments:
  --mode {reads,assembly,cds}
                        Pipeline mode, a.k.a the step from which the pipeline
                        is run
  --out OUT_DIR         Prefix for the output directory
  --overwrite           Overwrite the output if itexists. Do you really want
                        to use this feature? -- NOT YET IMPLEMENTED

Mode - READS:
  --single-end          In case of **Single-End reads**, use this option and
                        provide `--r1` only.
  --r1                  The first read of the pair, in FASTQ (foo_R1.fq[.gz])
                        format.
  --r2                  The second read of the pair, in FASTQ (foo_R2.fq[.gz])
                        format.
  --trimmomatic         Path to the executable `trimmomatic-<version>.jar`

Mode - ASSEMBLY:
  --transcripts         A file containing transcrits already assembled, in
                        FASTA format (bar.fa[.gz])

Mode - CDS:
  --cds                 File with the cds extracted from a set of transcripts,
                        in FASTA format (baz.fa[.gz])

KRYPTON run on HPC:
  --bucketin BUCKET_IN  Name of the bucket used to read data from. This option
                        is required to run KRYPTON on the HPC2 cluster
  --bucketout BUCKET_OUT
                        Name of the bucket used to store data in. This option
                        is required to run KRYPTON on the HPC2 cluster
  --run-on-HPC          Turn on this option when KRYPTON is meant to be run on
                        a HPC cluster
```

## Example

1. Basic example with the mode `reads`:

```bash
python3 bin/KRYPTON.py --out \<out_dir\> --r1 \<path/to/reads/\>read1.fq \
--r2 \<path/to/reads/\>read2.fq
```

- exemple mode "assembly" :

```bash

python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/assemblage chemin/absolu/output
```

- exemple mode "cds" :

```bash
python3.5 ./bin/KRYPTON.py assembly /chemin/absolu/fichier_cds chemin/absolu/output
```

### Résultats

For each step, the result are present under `<out_dir>` as follow:
- `<out_dir>/00_fastqc_raw/`: results FastQC on the raw reads
- `<out_dir>/01_trimmomatic/`: results of Trimmomatic
- `<out_dir>/02_fastqc_trimmed/`: results of FastQC on the cleaned reads
- `<out_dir>/03_trinity/`: Assembly of the reads

__WIP...__

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


### Commentaires :


Il peut avoir un problème avec MetaPathExplorer si la base de donnée utilisé par MetaPathExplorer n'est pas à jour, à surveiller.
