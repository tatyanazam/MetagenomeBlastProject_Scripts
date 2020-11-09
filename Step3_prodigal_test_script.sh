#!/bin/bash
#SBATCH --job-name=test_prod_array
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=800mb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tatyanaz@ufl.edu
#SBATCH --time=3-00:00:00
#SBATCH --output=test_prod_array_%A_%a.out
#SBATCH --array=1-8

module load seqtk
module load prodigal
date

#working directory = Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/
file_to_print=$(ls *.fasta | sed -n ${SLURM_ARRAY_TASK_ID}p)
echo $file_to_print
num_to_complete=$(cat $file_to_print | grep ">" | wc -l)
echo $num_to_complete

PER_TASK=$num_to_complete
START_NUM=1
END_NUM=$PER_TASK
echo This is task $SLURM_ARRAY_TASK_ID, which will do runs $START_NUM to $END_NUM

file_dir="${file_to_print%%.*}"
echo file_dir is $file_dir
file3="${file_dir%_*}"
echo name to use in blast ids_file is $file3

#ids_file= blast_res_ids_arc_top20_k_all.txt    
ids_file=blast_res_ids_${file3}_all.txt
echo ids_file is $ids_file
test_first_cont=$(head $ids_file)
echo $test_first_cont


for(( run=$START_NUM; run<=$END_NUM; run++ ))
do
    met_gen_id=$(cat $ids_file | sed -n ${run}p)
    echo $met_gen_id
    mkdir -p ${file_dir}/${met_gen_id}
    echo directory created
    echo $met_gen_id > seq_of_${met_gen_id}.txt
    seqtk subseq $file_to_print seq_of_${met_gen_id}.txt > ${file_dir}/${met_gen_id}/fasta_seq_${met_gen_id}_of_${file3}.fa
    echo seqtk performed
    rm seq_of_${met_gen_id}.txt 
    echo seq text removed
    prodigal -i ${file_dir}/${met_gen_id}/fasta_seq_${met_gen_id}_of_${file3}.fa -o ${file_dir}/${met_gen_id}/prodigal_res_${met_gen_id}_${file3}_genes -a ${file_dir}/${met_gen_id}/prodigal_res_${met_gen_id}_${file3}_proteins.faa -p meta
    echo prodigal performed on "$met_gen_id" for "$file_to_print" in "$file_dir"
    protein_file=${file_dir}/${met_gen_id}/prodigal_res_${met_gen_id}_${file3}_proteins.faa
    num_of_prot=$(cat $protein_file | grep ">" | wc -l)
    echo $num_of_prot
    print_out=$(paste <(echo "$met_gen_id") <(echo "$num_of_prot"))
    echo $print_out > ${file_dir}/total_protein_count_${met_gen_id}.txt
done
date
echo everything done now

date
