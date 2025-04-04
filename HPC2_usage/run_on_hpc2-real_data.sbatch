#!/bin/bash
#SBATCH --job-name=kry
#SBATCH --output=log/slurm-%j.out
#SBATCH --error=log/slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --partition=normal
#SBATCH --time=0-18:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G


# Setup the environment
module purge
module load gcc/8.1.0 ruby/2.4.2 hmmer/3.1b2 parallel/20151222
module load kofamscan/1.3.0
module load python/3.7.1 goofys/0.24.0

echo "START job:" `date`
echo "HOSTNAME:" `hostname`

# Setup the sample and DB
SAMPLE=CIL-AF
DB=SwissProt
MEM=62
# Setup the working directory and move in it
WORKDIR=/storage/scratch/$USER/${SLURM_JOB_ID}
RESDIR=KRY-${SAMPLE}-${SLURM_JOB_ID}

mkdir -p $WORKDIR
cd $WORKDIR

# Mount the buckets for data (input, output) and singularity container
B_INPUT=projet-cil
B_INPUT_DIR=$(mktemp -d -u -p '.' | sed 's/^\.\///')
B_INPUT_PATH=$WORKDIR/$B_INPUT_DIR
B_OUTPUT=damien
B_OUTPUT_DIR=$(mktemp -d -u -p '.' | sed 's/^\.\///')
B_OUTPUT_PATH=$WORKDIR/$B_OUTPUT_DIR
B_IMG=singularity_img
B_IMG_DIR=$(mktemp -d -u -p '.' | sed 's/^\.\///')
B_IMG_PATH=$WORKDIR/$B_IMG_DIR

mkdir -p $B_INPUT_PATH
mkdir -p $B_OUTPUT_PATH
mkdir -p $B_IMG_PATH

goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_INPUT $B_INPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_OUTPUT $B_OUTPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_IMG $B_IMG_PATH

### Note: Since Singularity v3.6, is the current working directory is not present
### within the container, Singularity is not trying to solve it anymore. So we
### have to use a mountpoint, throught the -B/--bind parameter.
### See here: https://github.com/apptainer/singularity/issues/5798

echo "Sample: $SAMPLE"

MP=/data

# R1=$B_INPUT_DIR/hq_reads/BK/CIL_BKOSRB_1_1_H7VC5DSXX.IND36_noribo_clean.fastq.gz
# R2=$B_INPUT_DIR/hq_reads/BK/CIL_BKOSRB_1_2_H7VC5DSXX.IND36_noribo_clean.fastq.gz
R1=$B_INPUT_DIR/hq_reads/AF/CIL_AFOSRB_1_1_H7VC5DSXX.IND30_noribo_clean.fastq.gz
R2=$B_INPUT_DIR/hq_reads/AF/CIL_AFOSRB_1_2_H7VC5DSXX.IND30_noribo_clean.fastq.gz

singularity exec -B $WORKDIR:$MP $B_IMG_DIR/krypton.code.sif KRYPTON.py \
    --r1 $MP/$R1 --r2 $MP/$R2 --out $MP/${RESDIR} \
    --mmseqs-annot --mmseqs-db-path $MP/${B_IMG_DIR}/database/mmseqs/$DB \
    --ko-annot $MP/${B_IMG_DIR}/database/ko -t $SLURM_CPUS_PER_TASK \
    --mem $MEM --bindpoint /data

## Run KoFamScan from HPC2
echo "Start KoFamScan from the HPC2 module and ${RESDIR}/run_kofamscan_hpc.sh" `date`
bash ${RESDIR}/run_kofamscan_hpc.sh

## Parse KoFamScan results
singularity exec -B $WORKDIR:$MP $B_IMG_DIR/krypton.code.sif \
    KRYPTON_parse_K0FamScan.py --project $MP/${RESDIR} \
    --files /usr/local/lib/python3.8/dist-packages/krypton/ressources/KEGG_data \
    --ko_list $MP/${B_IMG_DIR}/database/ko/ko_list

# Run MetaPathExplorer
echo "Start of MetaPathExplorer" `date`

## Prepare the ini file and run
cp $B_IMG_PATH/MetaPathExplorer.conf.ini .
sed -i "s@^outdir=\$@outdir=$MP/$RESDIR/10_MetaPathExplorer@" MetaPathExplorer.conf.ini

singularity exec -B $WORKDIR:$MP $B_IMG_DIR/MetaPathExplorer.sif \
    MetaPathExplorer --ini /data/MetaPathExplorer.conf.ini \
    --input matrix /data/$RESDIR/09_ko_annot/09_kofam_results.tsv.matrix_MPE.tsv

# A bit of cleanning
mv $HOME/MetaPathExplorer.log $RESDIR/10_MetaPathExplorer/MetaPathExplorer.log
rm -r $RESDIR/tmp

# Move the results back on the S3
echo "END computing:" `date`
mv $RESDIR $B_OUTPUT_PATH

# Clean evrything
fusermount -u $B_INPUT_PATH
fusermount -u $B_OUTPUT_PATH
fusermount -u $B_IMG_PATH

rm -r $WORKDIR

echo "END job:" `date`
