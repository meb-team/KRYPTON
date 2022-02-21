#!/bin/bash
#SBATCH --job-name=kry
#SBATCH --output=log/slurm-%j.out
#SBATCH --error=log/slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --partition=normal
#SBATCH --time=0-12:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G


# Setup the environment
module purge
module load gcc/8.1.0 ruby/2.4.2 hmmer/3.1b2 parallel/20151222
module load kofamscan/1.3.0
module load python/3.7.1 goofys/0.24.0

echo "START job:" `date`
echo "HOSTNAME:" `hostname`

echo "############## TEST ##############"
echo "Mem:" $SLURM_MEM_PER_NODE
echo "############## TEST ##############"


# Setup the working directory
SAMPLE="CIL_BK"
WORKDIR=/storage/scratch/$USER/${SLURM_JOB_ID}
RESDIR=$WORKDIR/KRY-${SAMPLE}

mkdir -p $WORKDIR

# Change to scratch
cd $WORKDIR

# Mount the buckets for data (input, output) and singularity container
B_INPUT=projet-cil
B_INPUT_PATH=$(mktemp -d -u -p $WORKDIR)
B_OUTPUT=damien
B_OUTPUT_PATH=$(mktemp -d -u -p $WORKDIR)
B_IMG=singularity_img

mkdir -p $B_INPUT_PATH
mkdir -p $B_OUTPUT_PATH
mkdir -p $B_IMG

goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_INPUT $B_INPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_OUTPUT $B_OUTPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_IMG $B_IMG

# Run KRYPTON
singularity exec $B_IMG/krypton.code.sif KRYPTON.py --r1 $B_INPUT_PATH/hq_reads/BK/CIL_BKOSRB_1_1_H7VC5DSXX.IND36_noribo_clean.fastq.gz \
    --r2 $B_INPUT_PATH/hq_reads/BK/CIL_BKOSRB_1_2_H7VC5DSXX.IND36_noribo_clean.fastq.gz \
    --out $RESDIR --mmseqs-annot --mmseqs-db UniRef90 \
    --mmseqs-db-path $B_IMG/database/mmseqs -t 16 --mem 60

# Run K0FamScan
exec_annotation -p $B_IMG/database/ko/profiles -k $B_IMG/database/ko/ko_list \
    --cpu $SLURM_CPUS_PER_TASK --mem 62

# Run MetaPathExplorer

# Move the results back on the S3

# Clean evrything
