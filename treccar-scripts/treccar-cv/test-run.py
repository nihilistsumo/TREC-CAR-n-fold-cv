'''
Created on Aug 13, 2018

@author: sumanta
'''

import os
import sys

out_dir = sys.argv[1]
test_runs_dir = sys.argv[2]

model_file = out_dir+"/models/all-train-model"
test_run_name = test_runs_dir.split("/")[len(test_runs_dir.split("/"))-1]
out_test_run_file = out_dir+"/out-runs/comb-"+test_run_name+"-run"

def read_runs(run_dir):
    runfiles = {}
    list_of_runfiles = sorted(os.listdir(run_dir))
    for fname in list_of_runfiles:
        rankings = {}
        f = open(run_dir+"/"+fname)
        line = f.readline()
        while line:
            line_elems = line.split()
            query = line_elems[0]
            para = line_elems[2]
            runscore = float(line_elems[4])
            if query in rankings.keys():
                rankings[query][para] = runscore
            else:
                para_score_dict = {para:runscore}
                rankings[query] = para_score_dict
            line = f.readline()
        for q in rankings.keys():
            q_dict = rankings.get(q)
            max_score = 0.0
            for p in q_dict.keys():
                if max_score<q_dict.get(p):
                    max_score = q_dict.get(p)
            for p in q_dict.keys():
                rankings.get(q)[p] = rankings.get(q)[p]/max_score
        runfiles[fname] = rankings
        f.close()
    print ("runfiles are read")
    return runfiles

opt_weights = []
model = open(model_file,'r')
for line in model:
    if not line.startswith("#"):
        weights = line.split()
        for i in range(len(weights)):
            opt_weights.append(weights[i].split(':')[1])
            
with open(out_test_run_file, "a") as outrun:
    test_runfiles = read_runs(test_runs_dir)
    test_queries = set()
    for f in test_runfiles.keys():
        test_rf = test_runfiles.get(f)
        for q in test_rf.keys():
            test_queries.add(q)
    for q in test_queries:
        paras_ret = set()
        for f in test_runfiles.keys():
            if q in test_runfiles.get(f).keys():
                para_scores = test_runfiles.get(f).get(q)
                for p in para_scores.keys():
                    paras_ret.add(p)
        for p in paras_ret:
            ret_score = 0
            fet_count = 0
            for f in test_runfiles.keys():
                if p in test_runfiles.get(f).get(q).keys():
                    ret_score = ret_score+float(test_runfiles.get(f).get(q).get(p))*float(opt_weights[fet_count])
                fet_count = fet_count+1
            outrun.write(q+" Q0 "+p+" 0 "+str(ret_score)+" COMB"+test_run_name+"\n")
print ("runfile written")