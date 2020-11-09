#!/usr/bin/env python3

import requests
requests.__version__

BASE='http://uniprot.org'
KB_ENDPOINT='/uniprot/'
TOOL_ENDPOINT='/uploadlists/'

genelist=open("prot_pres_5plustimes_for_uniprot.txt").readlines() #change to correct txt file name
for gene in genelist:
	payload={'query':'name:"' + gene.strip() + '"', 'format':'fasta', 'include':'yes'}
	result=requests.get(BASE + KB_ENDPOINT, params=payload)
	if result.ok:
		file=open(gene.strip()+"_test_oct2020.fasta",'w')
		file.write(result.text)
		file.close()
	else:
		print('Something went wrong: ', result.status_code)
		
