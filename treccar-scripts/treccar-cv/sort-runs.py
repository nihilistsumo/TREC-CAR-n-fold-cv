'''
Created on Aug 7, 2018

@author: sumanta
'''
import os
import sys

run_file = sys.argv[1]
out_file = sys.argv[2]
num_ret = int(sys.argv[3])

def sortrun(run_file):
    run_data = {}
    f = open(run_file)
    line = f.readline()
    while line:
        line_elems = line.split()
        runq = line_elems[0]
        runpara = line_elems[2]
        runscore = float(line_elems[4])
        paratuple = (runpara, runscore)
        if runq in run_data.keys():
            run_data[runq].append(paratuple)
        else:
            new_list = [paratuple]
            run_data[runq] = new_list
        line = f.readline()
    #run_data[fname] = scores
    for runq in run_data.keys():
        data = run_data[runq]
        data.sort(key=lambda tup: tup[1], reverse=True)
    f.close()
    return run_data

run_data = sortrun(run_file)
with open(out_file,"a+") as outrun:
    for q in run_data.keys():
        run_tuples = run_data.get(q)
        n = num_ret
        if num_ret>len(run_tuples):
            n = len(run_tuples)
        for i in range(n):
            para = run_tuples[i][0]
            score = run_tuples[i][1]
            outrun.write(q+" Q0 "+para+" "+str(i+1)+" "+str(score)+" SORTRUN\n")