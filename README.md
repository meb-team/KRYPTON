# KRYPTON

[![Build Status](https://github.com/meb-team/CRYPTON.git)](https://github.com/meb-team/CRYPTON)

## Introduction

This package, _euKaRYote ProtisT fOnctionnal aNnotation of transcriptome_,
abbreviated as _KRYPTON_, is a Python package containing a pipeline for
transcriptome assembly and annotation (functional and taxonomic).  
KRYPTON combines Trinity, MMseqs2 _clust_, MMseqs2 _search_ and MetaPathExplorer.

![Workflow KRYPTON](ressources/Workflow_KRYPTON.PNG)

## To-do list:

- [ ] **TransDecoder-Predict** capture the log and check if it ends correctly
        otherwise, re-run it with the parameter **`--no_refine_starts`**.
- [ ] Clarify the 3 steps: use the right vocabulary, eg "_peptide sequence_"
    instead of "_cds_"
- [ ] add a `requirements.txt`
- [ ] check if a step ended nicely?
    - [ ] trimmomatic output the information in STDOUT/STDERR
        (_TrimmomaticPE: Completed successfully_)
    - [ ] Trinity too ("_All commands completed successfully. :-)_")
- [ ] Tweak tool parameters by passing them to the command line:
    - [x] fastQC _--threads_
    - [ ] trimmomatic _MINLEN:32 SLIDINGWINDOW:10:20 LEADING:5 TRAILING:5_
    - [X] trinity _--CPU_ and _--max_memory_
    - [ ] MMseqs2: cluster mode; sensitivity, min seq ID, ...
    - [ ] TransDecoder --> min ORF size, Pfam annotation?
- [ ] Add a dict to store the subpath values
    - eg:
        - {"00" : "00_FastQC_raw",
        - "01" : "01_trimmomatic",
        - ... }
- <s>[ ] Output the logs in `self.output/xxx_log.log`, **not** `self.output/xxx/xxx_log.log`</s> **BAD IDEA**
- <s>[ ] Add the HMMER suite (TransDecoder?) + other step</s> **Not interesting**
- [ ] **PRIORITY** Add [AntiFam](https://github.com/ebi-pf-team/antifam)
to filter out spurious proteins after the second MMseqs clustering.
- [ ] Add [Phytool](https://caninuzzo.shinyapps.io/phytool_v1/) ??
- [ ] Add [Tiara](10.1093/bioinformatics/btab672) for the identification of
Eukaryotic data (_a.k.a_ it can remove prokaryotic sequences??) and moreover it
is supposed to distinguish nuclear and organellar sequences.

## Dependencies
- _All modes_
    - python >= 3.7
    - numpy >= 1.22
    - MMseqs2 v 10-6d92c

- _Mode reads_
    - fastQC >= 0.11.4
    - Trimmomatic >= 0.33
    - Trinity >= 2.9.1 and [Salmon](https://github.com/COMBINE-lab/salmon/releases/download/v1.0.0/Salmon-1.0.0_linux_x86_64.tar.gz) >= v1.0.0
        - I ran all my tests with **Trinity v2.9.1 which requires Salmon v1.0.0**
        - More recent version of Trinity may require Salmon > v1.0.0
        - The recipe for their [Docker image](https://hub.docker.com/r/trinityrnaseq/trinityrnaseq/tags) can help you choose the righ version of Salmon to use
        whether this information is not present in the Trinity's documentation.
    - [TransDecoder](https://github.com/TransDecoder/TransDecoder) >= 5.5.0

- _Mode assembly_
    - TransDecoder

- _Annotation_
    - KOFamScan >= v1.3, available on [KEGG](https://www.genome.jp/tools/kofamkoala/)
    via _ftp_ or _html_, with the HMM profiles.
    - [MetaPathExplorer](https://github.com/meb-team/MetaPathExplorer), to display
    the KEGG annotation on KEGG metabolic pathways.
        - **Do not** download the _release_ available which cannot handle TSV matrix.
        Instead use `git clone https://github.com/meb-team/MetaPathExplorer`
        - **Important note**: All dependencies **except one** are available on
        Conda (See below to install). The module _Config::IniFiles_ must be
        installed via _CPAN_: `cpan install Config::IniFiles`.

### Conda environment

To fill the requirements linked to Python, a recipe for a **Conda environment**
is present in the file `ressources/krypton_conda_env.yml`.

To install it, make sure you have a [Conda](https://docs.conda.io/) installed
on your system and run:

```bash
conda env create -f ressources/krypton_conda_env.yml
conda activate krypton_base
```

Then, several tools are available if you cannot or do not want to update your system:

```bash
#make sure you activated the Conda environment first
conda install fastqc trimmomatic=0.39 mmseqs2=13.45111  transdecoder=5.5.0

```

Unfortunately, _Trinity_ can't be installed in the same Conda environment,
so make sure it is available on your system.

## Install

```sh
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
pip install -e .
```

## Usage

There are several kind of usage. From the sequencing _reads_ (`--mode reads`), by
providing a set of transcripts (`--mode assembly`) or from a set of
**translated** CDS (`--mode cds`).

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

MMseqs2 options:
  --mmseqs-search-db    One of 1) Path to anexisting MMseqs2 database (Fast); 2) The name of a database provided by MMseqs2 (a list is present here https://github.com/soedinglab/MMseqs2/wiki#downloading-
                        databases - It can be long and take lot of disk space, eg UniRef90~=70GB); 3) Path to a FastA/Q[.gz] file, with the extension: .fa .fasta .fq or .fastq .pep and .gz or not. #####
                        Default = UniRef100
```

### Example

1. Basic example with the mode `reads`:

```bash
python3 bin/KRYPTON.py --out out_dir --r1 path/to/reads/read1.fq \
    --r2 path/to/reads/read2.fq
```

- Basic example with the mode `assembly`:

```bash
python3 bin/KRYPTON.py --mode assembly --transcripts path/to/transcripts/infile.fa[.gz] --out out_dir
```

- Basic example with the mode `cds`:

```bash
python3 ./bin/KRYPTON.py --mode cds --cds path/to/predicted/cds/infile.fa
```

### Results

For each step, the result are present under `<out_dir>` as follow:
- **Start of `read` mode**
    - `<out_dir>/00_fastqc_raw/`: results FastQC on the raw reads
    - `<out_dir>/01_trimmomatic/`: results of Trimmomatic
    - `<out_dir>/02_fastqc_trimmed/`: results of FastQC on the cleaned reads
    - `<out_dir>/03_trinity/`: Assembly of the reads
- **Start of `assembly` mode**
    - `<out_dir>/04_mmseqs/`: Clustering of the transcripts
    - `<out_dir>/05_transdecoder_longorfs/`: Predict the CDS from the transcripts
    - `<out_dir>/06_transdecoder_predict/`: Extract CDS that are most likely to code for a protein
- **Start of `cds` mode**
- `<out_dir>/07_mmseqs/`: Clustering of the CDS
- `<out_dir>/08_mmseq_search/`: Align the CDS (1 representative per cluster) against a reference database


<!--
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


Il peut avoir un problème avec MetaPathExplorer si la base de donnée utilisé par MetaPathExplorer n'est pas à jour, à surveiller. -->
