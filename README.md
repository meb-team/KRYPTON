# KRYPTON

[![Build Status](https://github.com/meb-team/KRYPTON.git)](https://github.com/meb-team/KRYPTON)

## Introduction

This package, _euKaRYote ProtisT fOnctionnal aNnotation of transcriptome_,
abbreviated as _KRYPTON_, written in Python, contains a pipeline for
transcriptome assembly and annotation (functional and taxonomic).  
KRYPTON combines Trinity, MMseqs2, KOFamScan and MetaPathExplorer.

<img src="ressources/Workflow_KRYPTON.PNG" width=400 units="px"></img>

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
    - [x] TransDecoder --> min ORF size, <s>Pfam annotation?</s>
- [ ] Add a dict to store the subpath values
    - eg:
        - {"00" : "00_FastQC_raw",
        - "01" : "01_trimmomatic",
        - ... }
- <s>[x] Output the logs in `self.output/xxx_log.log`, **not** `self.output/xxx/xxx_log.log`</s> **BAD IDEA**
- <s>[x] Add the HMMER suite (TransDecoder?) + other step</s> **Not interesting**
- [x] **PRIORITY** Add [AntiFam](https://github.com/ebi-pf-team/antifam)
to filter out spurious proteins after the second MMseqs clustering.
    - Included in the installation step
- [ ] Add [Phytool](https://caninuzzo.shinyapps.io/phytool_v1/) ??
- [ ] Add [Tiara](10.1093/bioinformatics/btab672) for the identification of
Eukaryotic data (_a.k.a_ it can remove prokaryotic sequences??) and moreover it
is supposed to distinguish nuclear and organellar sequences.

- [ ] leave the possibility to the user to use the script `krypton/tasks/ko_annot.py`
    - Add arguments parser for this script!


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

### With Conda environment

To fill the requirements linked to Python, a recipe for a **Conda environment**
is present in the file `ressources/krypton_conda_env.yml`.

1. Setup

To install it, make sure you have a [Conda](https://docs.conda.io/) installed
on your system first and then runs:

```bash
conda env create -f ressources/krypton_conda_env.yml
conda activate krypton_base # Activate the Conda environment
```

2. Core tools

```bash
cpan install Config::IniFiles # For MetaPathExplorer
```

3. KRYPTON code

Move in the directory where you want to setup KRYPTON first.  
Then:

```bash
git clone https://github.com/meb-team/KRYPTON.git
cd KRYPTON
pip install -e .
```

4. Data for [Antifam](https://xfam.wordpress.com/2012/03/21/introducing-antifam/):

```bash
cd ressources/
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/AntiFam/current/Antifam.tar.gz
tar -zxf Antifam.tar.gz
rm relnotes version *.seed AntiFam_* Antifam.tar.gz
hmmpress AntiFam.hmm
cd ..
```

5. Data for KEGG annotation

```bash
python bin/download_KEGG_data.py
```

6. Trinity

Unfortunately, _Trinity_ versions > 2.8.5 can't be installed in the same Conda
environment, so make sure it is available on your system. Sorry.

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
