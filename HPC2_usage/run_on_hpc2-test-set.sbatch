#!/bin/bash
#SBATCH --job-name=kry
#SBATCH --output=log/slurm-%j.out
#SBATCH --error=log/slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --partition=debug
#SBATCH --time=0-00:55:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G


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
SAMPLE="test_set"

WORKDIR=/storage/scratch/$USER/${SLURM_JOB_ID}
RESDIR=KRY-${SAMPLE}-${SLURM_JOB_ID}

mkdir -p $WORKDIR

# Change to scratch
cd $WORKDIR

# Copy test data
cp $HOME/data/kry_test_set/CIL_noribo_r?.fq .

# Mount the buckets for data (input, output) and singularity container
# B_INPUT=projet-cil
# B_INPUT_PATH=$(mktemp -d -u -p $WORKDIR)
B_OUTPUT=damien
B_OUTPUT_PATH=$(mktemp -d -u -p $WORKDIR)
B_IMG=singularity_img

# mkdir -p $B_INPUT_PATH
mkdir -p $B_OUTPUT_PATH
mkdir -p $B_IMG

# goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
#     --dir-mode=0777 --file-mode=0777 --cheap \
#     --endpoint https://s3.mesocentre.uca.fr $B_INPUT $B_INPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_OUTPUT $B_OUTPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_IMG $B_IMG

### Note: Since Singularity v3.6, is the current working directory is not present
### within the container, Singularity is not trying to solve it anymore. So we
### have to use a mountpoint,throught the -B/--bind option
### See here: https://github.com/apptainer/singularity/issues/5798

MP=/data

# Run KRYPTON
singularity exec -B $WORKDIR:$MP $B_IMG/krypton.code.sif KRYPTON.py \
    --r1 $MP/CIL_noribo_r1.fq --r2 $MP/CIL_noribo_r2.fq --out $MP/$RESDIR \
    --mmseqs-annot --mmseqs-db UniProtKB/Swiss-Prot \
    --mmseqs-db-path $MP/${B_IMG}/database/mmseqs \
    -t $SLURM_CPUS_PER_TASK --mem 30

# Run K0FamScan
exec_annotation -p $B_IMG/database/ko/profiles -k $B_IMG/database/ko/ko_list \
    --cpu $SLURM_CPUS_PER_TASK -f detail-tsv \
    -o $RESDIR/09_ko_annot/09_kofam_results.tsv $RESDIR/07_mmseqs_antifam/good_proteins.fa

# Run MetaPathExplorer
##later



# Move the results back on the S3
echo "END computing:" `date`
mv $RESDIR $B_OUTPUT_PATH

# Clean evrything
# fusermount -u $B_INPUT_PATH
fusermount -u $B_OUTPUT_PATH
fusermount -u $B_IMG

rm -r $WORKDIR
echo "END job:" `date`
