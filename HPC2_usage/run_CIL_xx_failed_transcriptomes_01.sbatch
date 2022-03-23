#!/bin/bash
#SBATCH --job-name=CIL-B
#SBATCH --output=log/slurm-%A_%a.out
#SBATCH --error=log/slurm-%A_%a.err
#SBATCH --ntasks=1
#SBATCH --partition=long
#SBATCH --time=7-00:00:00
#SBATCH --mail-user=damien.courtine@uca.fr
#SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE,STAGE_OUT,TIME_LIMIT_50,TIME_LIMIT_90,ARRAY_TASKS
#SBATCH --cpus-per-task=16
#SBATCH --mem=48000M
#SBATCH --array=0-2

# Setup the environment
module purge
module load gcc/8.1.0 ruby/2.4.2 hmmer/3.1b2 parallel/20151222
module load kofamscan/1.3.0
module load python/3.7.1 goofys/0.24.0

echo "START job:" `date`
echo "HOSTNAME:" `hostname`

# Setup the DB and quantity of RAM
DB=uniref90DB
MEM=44

echo "Database for MMseqs2: $DB"

# Setup the working directory and move in it
WORKDIR=/storage/scratch/$USER/${SLURM_JOB_ID}-${SLURM_ARRAY_TASK_ID}
mkdir -p $WORKDIR
cd $WORKDIR

echo "move in $WORKDIR"

# Mount the buckets for data (input; output) and Singularity container
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

echo "Input: $B_INPUT ; $B_INPUT_DIR ; $B_INPUT_PATH"
echo "Output: $B_OUTPUT ; $B_OUTPUT_DIR ; $B_OUTPUT_PATH"
echo "Imgs: $B_IMG ; $B_IMG_DIR ; $B_IMG_PATH"

## Files in buckets input and output can ONLY be READ
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --file-mode 0444 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_INPUT $B_INPUT_PATH
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --file-mode 0444 --cheap \
    --endpoint https://s3.mesocentre.uca.fr $B_OUTPUT $B_OUTPUT_PATH
## Files for Singularity and Databases can be READ and EXECUTED
goofys --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid $UID -gid $(id -g) \
    --file-mode 0544 --endpoint https://s3.mesocentre.uca.fr $B_IMG $B_IMG_PATH

## Where are the reads?
DATA=$B_INPUT_DIR/hq_reads
echo "Data in: $DATA"

## Arrays
#### Beware when declaring an array based on expression!!!
#### DO NOT FORGET the surrounding PARENTHESIS!!!
# samples=($(find $DATA -type d -name "B?"))
samples=("AC" "BE" "CD")

# echo -e "samples:\n${samples[@]::SLURM_ARRAY_TASK_COUNT}"

CURRENT=$(basename ${samples[$SLURM_ARRAY_TASK_ID]})
echo -e "Now get the R1 and R2 for the current sample $CURRENT\nfrom ${samples[$SLURM_ARRAY_TASK_ID]}"
R1=$(find ${DATA}/${samples[$SLURM_ARRAY_TASK_ID]} -type f -name "*_?_1_*.fastq.gz")
R2=$(find ${DATA}/${samples[$SLURM_ARRAY_TASK_ID]} -type f -name "*_?_2_*.fastq.gz")

ls -l $R1 $R2

echo -e "R1 = $R1 \nR2 = $R2"

## Define the directory to write the output
RESDIR=CIL-${CURRENT}_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}
MP=/data

echo "KRYPTON will use the directory $RESDIR for the parameter --out"

singularity exec -B $WORKDIR:$MP $B_IMG_DIR/krypton.code.sif KRYPTON.py \
    --r1 $MP/$R1 --r2 $MP/$R2 --out $MP/${RESDIR} \
    --mmseqs-annot --mmseqs-db-path $MP/${B_IMG_DIR}/database/mmseqs/$DB \
    --ko-annot $MP/${B_IMG_DIR}/database/ko -t $SLURM_CPUS_PER_TASK \
    --mem $MEM --bindpoint $MP

## Run KoFamScan from HPC2
echo "Start KoFamScan from the HPC2 module and ${RESDIR}/run_kofamscan_hpc.sh"
echo `date`
bash ${RESDIR}/run_kofamscan_hpc.sh

## Parse KoFamScan results
echo "Parse KoFamScan data"
singularity exec -B $WORKDIR:$MP $B_IMG_DIR/krypton.code.sif \
    KRYPTON_parse_K0FamScan.py --project $MP/${RESDIR} \
    --files /usr/local/lib/python3.8/dist-packages/krypton/ressources/KEGG_data \
    --ko_list $MP/${B_IMG_DIR}/database/ko/ko_list

# ## Run MetaPathExplorer
# echo "Start of MetaPathExplorer" `date`
#
# ## Prepare the ini file and run
# cp $B_IMG_PATH/MetaPathExplorer.conf.ini .
# sed -i "s@^outdir=\$@outdir=$MP/$RESDIR/10_MetaPathExplorer@" MetaPathExplorer.conf.ini
#
# singularity exec -B $WORKDIR:$MP $B_IMG_DIR/MetaPathExplorer.sif \
#     MetaPathExplorer --ini /data/MetaPathExplorer.conf.ini \
#     --input matrix /data/$RESDIR/09_ko_annot/09_kofam_results.tsv.matrix_MPE.tsv

echo "END computing:" `date`

## A bit of cleanning
# mv $HOME/MetaPathExplorer.log $RESDIR/10_MetaPathExplorer/MetaPathExplorer.log
echo "Cleaning Trinity logs from the unused reads..."

cat $RESDIR/03_trinity/03_trinity_logs.log | sed  '/skipping/d' | uniq >$RESDIR/03_trinity/03_trinity_logs-clean.log
rm $RESDIR/03_trinity/03_trinity_logs.log
rm -r $RESDIR/tmp

# Move the results back on the S3
echo "Move results in the bucket $B_OUTPUT"
mv $RESDIR $B_OUTPUT_PATH


echo "Unmount the buckets"
fusermount -u $B_INPUT_PATH
fusermount -u $B_OUTPUT_PATH
fusermount -u $B_IMG_PATH

echo "wait 10 s..."
sleep 10

echo "remove $WORKDIR"
rm -r $WORKDIR

echo "END job:" `date`
