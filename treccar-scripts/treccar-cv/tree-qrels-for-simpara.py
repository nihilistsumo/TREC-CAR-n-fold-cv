'''
Created on Aug 10, 2018

This will convert tree.qrels to disjoint type tree.qrels which means paragraphs do not overlap
between two levels of sections in same page; this is needed for paragraph similarity tasks

@author: sumanta
'''

import os
import sys

tree_qrels = sys.argv[1]
out_simpara_qrels = sys.argv[2]

def read_qrels(qrels_path):
    qrels_dict = {}
    qrels_file = open(qrels_path, 'r')
    for line in qrels_file:
        q = line.split()[0]
        page = q.split("/")[0]
        p = line.split()[2]
        if page in qrels_dict.keys():
            if q in qrels_dict[page].keys():
                qrels_dict[page][q].add(p)
            else:
                new_paras = set()
                new_paras.add(p)
                qrels_dict[page][q] = new_paras
        else:
            new_paras = set()
            new_paras.add(p)
            new_dict = {q:new_paras}
            qrels_dict[page] = new_dict
    qrels_file.close()
    return qrels_dict

def convert_simpara_qrels(tree_qrels_dict):
    reversed_simpara_qrels_dict = {}
    for page in tree_qrels_dict.keys():
        reversed_qrels = {}
        for q in tree_qrels_dict[page].keys():
            for p in tree_qrels_dict[page][q]:
                if p not in reversed_qrels.keys() or len(reversed_qrels[p].split("/"))<len(q.split("/")):
                    reversed_qrels[p] = q
        reversed_simpara_qrels_dict[page] = reversed_qrels    
    return reversed_simpara_qrels_dict
                
            
tree_qrels_dict = read_qrels(tree_qrels)
rev_simpara_qrels_dict = convert_simpara_qrels(tree_qrels_dict)
with open(out_simpara_qrels,'a+') as sim_q:
    for page in rev_simpara_qrels_dict.keys():
        for p in rev_simpara_qrels_dict[page].keys():
            q = rev_simpara_qrels_dict[page][p]
            sim_q.write(q+" 0 "+p+" 1\n")
            
