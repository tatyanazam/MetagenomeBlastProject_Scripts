#!/bin/bash
#SBATCH --job-name=emapp_clean30_8cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=15gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tatyanaz@ufl.edu
#SBATCH --time=30-00:00:00
#SBATCH --output=emapp_clean_allabove30_apr3_16cpu_%j.out

module load seqtk
module load prodigal
module load eggnog-mapper
date

#working directory = Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/
ids_file=prodnew_allabove30_allmetscaff.txt
echo ids_file is $ids_file
test_first_cont=$(head $ids_file)
echo $test_first_cont

pfam_dir=/ufrc/data/reference/pfam/current
echo $pfam_dir

START_NUM=1
END_NUM=$(cat $ids_file | wc -l)
echo $START_NUM
echo $END_NUM

for(( run=$START_NUM; run<=$END_NUM; run++ ))
do
    protein_file=$(cat $ids_file | sed -n ${run}p)
    echo $protein_file
    emapper.py --cpu 16 -i $protein_file -o ${protein_file}_eggmap_results -m diamond
    echo eggnogmapper performed for $met_gen_id 
done
date
