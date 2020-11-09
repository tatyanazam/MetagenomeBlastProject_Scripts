#!/bin/bash
#SBATCH --job-name=get_blast_seq
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=40gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tatyanaz@ufl.edu
#SBATCH --time=2-00:00:00
#SBATCH --output=get_blast_seq_from_db_%j.out
module load ncbi_blast
date

db_1="all_files_part1_1_to_5_out_db"
db_2="all_files_part2_6_to_10_out_db"


for file in Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/*.log
do
    #file #Hub_Seq_Top_Names/Blast_Log_results/take1_hy_top20_unk_hubs.fa_all_files_part1_1_to_5_out_db_blast_test.log
    echo $file
    file2="${file%%.*}"  #Hub_Seq_Top_Names/Blast_Log_results/take1_hy_top20_unk_hubs
    file3="${file##*/}"     #take1_hy_top20_unk_hubs.fa_all_files_part1_1_to_5_out_db_blast_test.log
    just_name="${file2##*/}"    #take1_hy_top20_unk_hubs
    echo $just_name
    awk '{print $2}' $file > Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/blast_res_ids_${just_name}.txt
    echo blast ids file created for "$file" and called "blast_res_ids_${just_name}.txt"
    if echo $file2 | grep -Eq 'take1'
    then
        echo take1 file "$file2" so use "$db_1" only
        blastdbcmd -db $db_1 -entry_batch Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/blast_res_ids_${just_name}.txt -outfmt %f > Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/blast_seqs_${just_name}_${db_1}.fasta
        echo sequences from blast db "$db_1" for "$file" retrieved and stored in new file
        date
    else
        echo take2 file "$file2" so use "$db_2" only
        blastdbcmd -db $db_2 -entry_batch Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/blast_res_ids_${just_name}.txt -outfmt %f > Hub_Seq_Top_Names/Blast_Log_results/Blast_Log_res_final/blast_seqs_${just_name}_${db_2}.fasta
        echo sequences from blast db "$db_2" for "$file" retrieved and stored in new file
        date
    fi
echo sequences retrieved from databases for all files
done
echo everything complete - all blast seq retrieved and stored in new files
date
