#!/bin/bash
#SBATCH --job-name=test_assemblage_clusterisation_traduction
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.out
#SBATCH --ntasks=1
#SBATCH --time=72:00:00
#SBATCH --partition=smp
#SBATCH --mem=1024G
#SBATCH --cpus-per-task=20
#SBATCH --array=0,1
#SBATCH --mem-per-cpu=4755M


module purge
IFS=$'\n\t'


# Set up whatever package we need to run with
module purge

module load gcc/8.1.0
module load java/oracle-1.8.0_45
module load bowtie2/2.3.4.3
module load samtools/1.9
module load bcftools/1.9
module load jellyfish/2.2.10
module load tbb/2019.3
module load salmon/0.12.0


#fastqc
module load fastqc/0.11.4
fastqc --version


#trimmomatic
module load trimmomatic/0.33
java -jar /opt/apps/trimmomatic-0.33/trimmomatic-0.33.jar --version




#trinity
module load trinityrnaseq/2.9.1
Trinity --version


#python
module load python/3.7.1
python --version

module load goofys/0.19.0

#numpy
module load numpy/1.18.1

#mmseqs2
module load MMseqs2/10-6d92c

#parallel
module load parallel/20151222




## Declare functions
function error {
    error=$1
    date=$(date "+%Y-%m-%d %H:%M:%S")
    if ! [ -z $2 ]; then 
        usage
        >&2 echo "error: $error"
    else 
        >&2 echo "[$date] ERROR: $error. Execution halted."
        end=$(date +%s)
        warning "Runtime: $((end-start)) sec"
    fi
    exit 1
}

function warning {
    message=$@
    date=$(date "+%Y-%m-%d %H:%M:%S")
    >&2 echo "[$date] INFO: $message"
}

function exit_step {
    dir=$1
    fusermount -u $dir
    rmdir $dir
    exit 0 
}

function usage {
    >&2 echo "usage: sbatch --array 1-N $filename [-h] [-b BUCKET] [-p PROFILE]
                                         [--readsId [0-100]]"
}

function help {
    >&2 echo "
                ...::: $filename v$__version__ :::...
            "
    usage
    >&2 echo "
Recruting reads against genome assembly file. 

Optional arguments:
    -h, --help              Print this help and exit.
    -f, --force-overwrite   Force bam files owerwriting. 
    --metrics               Produce metrics file.
    -r, --readsId [0-100]   Reads identity cutoff to keep alignement [95.00].

Required arguments:
    -a, --assembly          Path to genome assembly list file.
    -an, --assembly-nb      Assembly number to process. 
    -b, --bucket            Named of the bucket to store/check the data.
    -p, --profile           Profile to access bucket in credential file. 
    -s, --sample-project    Reads sample project {sola,redsea}.

Written by Corentin Hochart (corentin.hochart@uca.fr), UMR CNRSS 6023
Laboratoire Genome et Environement (LMGE). Released under the terms of the GNU
General Public License v3. $filename version $__version__.    
    "
    exit 1
}


calc(){ awk "BEGIN { print "$*" }"; }

## Print wrapper usage if no arguments
if [ ! $1 ];then
    usage
    exit 1
fi

## Greet the user
start=$(date +%s)
date=$(date)
warning "Date : $date"
date=$(date +%Y%m%d)
warning "Hi $USER. Lets do some good job together"

## Get options
arguments=$@
force_overwrite=false
metrics=false
readsId='95.00'

while test $# -gt 0; do
    case "$1" in
        -h|--help)
            help
            exit 0;
            ;;
        -a|--assembly)
            shift
                if test $# -gt 0; then
                    export assembly_file=$1
                else 
                    error 'argument -a/--assembly: expected one argument' usage
                fi
            shift
            ;;
        -an|--assembly-nb)
            shift
                if test $# -gt 0; then
                    export assembly_number=$1
                else 
                    error 'argument -an/--assembly-nb: expected one argument' usage
                fi
            shift
            ;;
        -b|--bucket)
            shift
                if test $# -gt 0; then
                    export bucket_name=$1
                else 
                    error 'argument -b/--bucket: expected one argument' usage
                fi
            shift
            ;;
        -bo|--bucketout)
            shift
                if test $# -gt 0; then
                    export bucketout_name=$1
                else
                    error 'argument -bo/--bucketout: expected one argument' usage
                fi
            shift
            ;;
        -f|--force-overwrite)
            shift
            force_overwrite=true
            ;;
        --metrics)
            shift
            metrics=true
            ;;
        -p|--profile)
            shift
                if test $# -gt 0; then
                    export profile=$1
                else 
                    error 'argument -p/--profile: expected one argument' usage
                fi
            shift
            ;;
        -r|--readsId)
            shift
                if test $# -gt 0; then
                    export readsId=$1
                else 
                    error 'argument -r/--readsId: expected one argument' usage
                fi
            shift
            ;;
        -s|--sample-project)
            shift
                if test $# -gt 0; then
                    export sample_project=$1
                else 
                    error 'argument -s/--sample-project: expected one argument' usage
                fi
            shift
            ;;
        *)
            error "Unknown option $1" 
            break
            ;;
    esac
done


## Create mount / working dir 
warning "Mount distant directory."
mount_dir=$(mktemp -d)
unset http_proxy
unset https_proxy
mkdir -p $mount_dir
goofys --profile $profile --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid 5471 -gid 5001 --dir-mode=555 --file-mode=555 --cheap --endpoint https://s3.mesocentre.uca.fr $bucket_name $mount_dir

warning "Create working directory."
working_dir=/storage/scratch/anauclair3/$SLURM_JOB_ID
TMPDIR=$working_dir/tmp
mkdir -p $TMPDIR
TMP=$TMPDIR
TEMP=$TMPDIR
export TMPDIR TMP TEMP


#Noribo data
reads_folder_pathway=$mount_dir/hq_reads/

#Ribo data
#reads_folder_pathway=$mount_dir/hq_reads_ribo/AA



ls $mount_dir
ls $reads_folder_pathway
echo $reads_folder_pathway

#echo $max_memory




#tabfor=($(find "$reads_folder_pathway"/ -type f -name "*_?_1_*.fastq.gz"))
#tabrev=($(find "$reads_folder_pathway"/ -type f -name "*_?_2_*.fastq.gz"))

#pour les fichiers Test noribo
tabfor=($(find "$reads_folder_pathway"/ -type f -name "*_?_1.*.fastq.gz"))
tabrev=($(find "$reads_folder_pathway"/ -type f -name "*_?_2.*.fastq.gz"))



printf '%s\n' "${tabfor[@]}"
printf '%s\n' "${tabrev[@]}"

echo ${tabfor[$SLURM_ARRAY_TASK_ID]}
echo ${tabrev[$SLURM_ARRAY_TASK_ID]}

#sample_name=$(echo ${tabfor[$SLURM_ARRAY_TASK_ID]} | cut -d '/' -f5)

#pour les fichiers Test noribo
sample_name=$(echo ${tabfor[$SLURM_ARRAY_TASK_ID]} | cut -d '/' -f6) 


echo $sample_name
#echo $INPUT



fichier_forward_decompresse=$(mktemp)
gunzip -c ${tabfor[$SLURM_ARRAY_TASK_ID]} > $fichier_forward_decompresse

fichier_reverse_decompresse=$(mktemp)
gunzip -c ${tabrev[$SLURM_ARRAY_TASK_ID]} > $fichier_reverse_decompresse

#wc -l $fichier_forward_decompresse
#wc -l $fichier_reverse_decompresse

echo "C est le working_dir"
ls $working_dir
echo " "

mkdir -p $working_dir/$sample_name

python /home/anauclair3/KRYPTON_Assemblage_Clusterisation_Traduction_07_06_2021.py reads "$fichier_forward_decompresse" "$fichier_reverse_decompresse" $working_dir/$sample_name


## Create mount / working dir
warning "Mount distant directory."
mount_dir2=$(mktemp -d)
unset http_proxy
unset https_proxy
mkdir -p $mount_dir2
goofys --profile $profile --stat-cache-ttl 3600s --type-cache-ttl 3600s -uid 5471 -gid 5001 --dir-mode=0777 --file-mode=0777 --cheap --endpoint https://s3.mesocentre.uca.fr $bucketout_name $mount_dir2


echo "C est le mount_dir2"
echo " "
ls $mount_dir2

mkdir -p $mount_dir2/$sample_name"_noribo"

cp -r $working_dir/$sample_name $mount_dir2/$sample_name"_noribo"

#ls $mount_dir2



# Clean and unmount directory
warning 'Unmount directory'
cd
exit_step $mount_dir2


#ls $working_dir


# Clean and unmount directory
rm -r $working_dir
warning 'Unmount directory'
cd
exit_step $mount_dir
