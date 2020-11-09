#!/bin/bash
#SBATCH --job-name=uniprot_test    # Job name
#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=tatyanaz@ufl.edu     # Where to send mail  
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --mem=1gb                     # Job memory request
#SBATCH --time=2-00:00:00               # Time limit hrs:min:sec
#SBATCH --output=uniprot_test_%j.log   # Standard output and error log
pwd; hostname; date

module load python3

echo "Running script to get back fasta files of all uniprot terms matching protein name"

python get_back_uniprot_fasta_seq.py

date
