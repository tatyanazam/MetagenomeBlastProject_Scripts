#!/bin/bash
#SBATCH --job-name=blast_top50
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tatyanaz@ufl.edu
#SBATCH --time=1-00:00:00
#SBATCH --output=blast_top50_hubs_against_db_%j.out
module load ncbi_blast
date

db_1="all_files_part1_1_to_5_out_db"
db_2="all_files_part2_6_to_10_out_db"

for file in Hub_Seq_Top_Names/*.fa
do 
    file2="${file%%.*}"
    file3="${file##*/}"
    echo $file2
    echo $file3
    #blastn -query Hub_Seq_Top_Names/hs_top50_unk_hubs.fa -db all_files_part1_1_to_5_out_db -perc_identity 95 -outfmt 6 > Hub_Seq_Top_Names/Blast_Log_results/all_files_part1_hs_50_unk_blast_test.log
    blastn -query $file -db $db_1 -perc_identity 95 -outfmt 6 > Hub_Seq_Top_Names/Blast_Log_results/take1_${file3}_${db_1}_blast_test.log
    echo blast done for "$db_1" and "$file3"
    blastn -query $file -db $db_2 -perc_identity 95 -outfmt 6 > Hub_Seq_Top_Names/Blast_Log_results/take2_${file3}_${db_2}_blast_test.log 
    echo blast done for "$db_2" and "$file3"
done



date
