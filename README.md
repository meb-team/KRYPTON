# KRYPTON

## Introduction

This package, _euKaRYote ProtisT fOnctionnal aNnotation of transcriptome_,
abbreviated as _KRYPTON_, written in Python, contains a pipeline for
transcriptome assembly and annotation (functional and taxonomic).  
KRYPTON combines Trinity, MMseqs2, KOFamScan and MetaPathExplorer.

<img src="krypton/ressources/workflow.png" width=400 units="px"></img>

<!-- ## Dependencies

- _All modes_
    - python >= 3.8
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
        installed via _CPAN_: `cpan install Config::IniFiles`. -->

## Install

### With Conda environment - **Preferred way**

:warning: :warning: The Conda env seems broken... I have to fix it
:warning: :warning:

There is a recipe for a _Conda_ environment in here : `krypton/ressources/krypton_conda_env.yml`

Otherwise, here is the command to build it:

```bash
conda create -n krypton
conda install -c bioconda -c conda-forge -y python numpy fastqc trimmomatic kofamscan mmseqs2
```

1. Setup

To install it, make sure you have a [Conda](https://docs.conda.io/) installed
on your system first and then runs:

```bash
conda env create -f ressources/krypton_conda_env.yml
conda activate krypton_base # Activate the Conda environment
```

2. KRYPTON code

Move in the directory where you want to setup _KRYPTON_ first. Then:

```bash
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
pip install -e .
```

3. Data for [Antifam](https://xfam.wordpress.com/2012/03/21/introducing-antifam/):

```bash
cd krypton/ressources/
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/AntiFam/current/Antifam.tar.gz
tar -zxf Antifam.tar.gz
rm relnotes version *.seed AntiFam_* Antifam.tar.gz
hmmpress AntiFam.hmm
cd ../..
```

4. Data for _KoFamScan_

```bash
python KRYPTON_download_K0famScan_data.py
```

### On you system (not recommended)

**- WIP -**

## Usage

There are several kind of usage. From the sequencing _reads_ (`--mode reads`), by
providing a set of transcripts (`--mode assembly`) or from a set of
**translated** CDS (`--mode cds`).

The help menu is available with the command `python bin/KRYPTON.py -h`.

## Example

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
  - `<out_dir>/08_mmseq_search/`: Align the CDS (1 representative per cluster)
    against a reference database
  - `<out_dir>/09_ko_annot/`: KOFamScan results
  - `<out_dir>/10_MetaPathExplorer/`: MetaPathExplorer results

## Tips

### Run on HPC via a Singularity container

As TransDecoder.Predict outputs its results in the Current Working directory
(CWD) like it is not possible to pass it such information... I had to find a way
to move those files within the correct directory. So I adapted the KRYPTON's
code to use it within a Singularity container. To this mean, I added a
parameter, `--bindpoint` which informs KRYPTON about the path used
to link the host to the container.

In fact, TransDecoder.Predict write its results in `$HOME`, which is very weird
but the main author will not fix that as he moved to another position... So
I have to update the KRYPTON's code to handle this exception.

For the moment, formatting a MMseqs DB with KRYPTON running in a Singularity
container and saving it on CEPH server seems impossible... That is why
I let KRYPTON doing the formatting within the result directory and I copy
the database on CEPH after.

# Temp

```bash
mamba create -n toto "trinity>=2.9.1"
mamba install fastqc kofamscan mmseqs2
mamba install "transdecoder==5.5.0"

KRYPTON.py --out test01 \
    --r1 ../test/data/files_test_reads/CIL_AAOSRB_1_1_H7VC5DSXX.IND1_noribo_clean_test10.fastq \
    --r2 ../test/data/files_test_reads/CIL_AAOSRB_1_2_H7VC5DSXX.IND1_noribo_clean_test10.fastq \
    -t 8

## ran complete in less than 5mn, so we are good

### THEN, MMSEQS annotation : Swissprot for the test
### TRY kofamscan : what is produced, can I parse it?

KRYPTON.py --out test02  --cds prot.fa --no-cds-cluster --mmseqs-annot \
  --mmseqs-db-path $HOME/databases/mmseqs/Swiss-ProtDB -t8

# I have the error "Mode - READS:", so let's investigate there first.

```
