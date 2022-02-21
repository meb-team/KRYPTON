#!/bin/bash
#SBATCH --job-name=dl_K0
#SBATCH --output=log/slurm-%j.out
#SBATCH --error=log/slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --partition=fast
#SBATCH --time=0-2:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G


# Setup the environment
module purge
module load gcc/8.1.0 python/3.7.1 goofys/0.24.0

echo "START job:" `date`
echo "HOSTNAME:" `hostname`

# Setup the working directory
WORKDIR=/storage/scratch/$USER/${SLURM_JOB_ID}
mkdir -p $WORKDIR

# Change to scratch
cd $WORKDIR

# Mount the buckets for data (input, output) and singularity container
B_IMG=singularity_img

mkdir -p $B_IMG

goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --dir-mode=0777 --file-mode=0777 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_IMG $B_IMG

echo "START dl:" `date`

# DL via the script within KRYPTON
singularity exec $B_IMG/krypton.code.sif KRYPTON_download_K0famScan_data.py \
      $B_IMG/database/ko

# Clean everything
echo "END dl:" `date`

fusermount -u $B_IMG
cd $HOME
rm -r $WORKDIR
echo "END job:" `date`
