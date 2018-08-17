'''
Created on Aug 7, 2018

This script splits the tree qrels into 5 folds using the benchmarkY1 train fold-*-qrels files

@author: sumanta
'''

import os
import sys

trec_dir = sys.argv[1]
qrels_suffix = sys.argv[2]
tree_qrels_file = sys.argv[3]
out_dir = sys.argv[4]

tree_qrels_suffix = tree_qrels_file.split('/')[len(tree_qrels_file.split('/')-1)]
for fold in range(5):
    qrels_file = open(trec_dir+"/fold-"+str(fold)+"-"+qrels_suffix, 'r')
    qrels_pages = set()
    for line in qrels_file:
        page = line.split()[0].split('/')[0]
        qrels_pages.add(page)
    qrels_file.close()
    
    with open(out_dir+"/fold-"+str(fold)+"-"+tree_qrels_suffix,'a+') as tfqrels:
        tqrels = open(tree_qrels_file,'r')
        for line in tqrels:
            if(line.split().split('/') in qrels_pages):
                tfqrels.write(line+"\n")
        tqrels.close()

print ("qrels file is read")