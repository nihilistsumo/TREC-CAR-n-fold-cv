'''
Created on Aug 6, 2018

@author: sumanta
'''
import os
import sys
import subprocess

#arguments: treccar-dataset-directory runfiles-directory fold-n/test Ranklib-directory qrels-file-suffix

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ("Error: Creating directory: " + directory)
        
def read_qrels(qrels_dir, qrels_suffix, test_fold_no): 
    qrels_dict = {} 
    for fold in range(5):
        if str(fold) != test_fold_no:
            qrels_file = open(qrels_dir+"/fold-"+str(fold)+"-"+qrels_suffix, 'r')
            for line in qrels_file:
                q = line.split()[0]
                p = line.split()[2]
                if q in qrels_dict.keys():
                    qrels_dict.get(q).add(p)
                else:
                    new_paralist = set()
                    new_paralist.add(p)
                    qrels_dict[q] = new_paralist
            qrels_file.close()
    print ("qrels file is read") 
    return qrels_dict

def read_qrels_full(qrels_dir, qrels_suffix):
    qrels_dict = {}
    qrels_file = open(qrels_dir+"/"+qrels_suffix, 'r')
    for line in qrels_file:
        q = line.split()[0]
        p = line.split()[2]
        if q in qrels_dict.keys():
            qrels_dict.get(q).add(p)
        else:
            new_paralist = set()
            new_paralist.add(p)
            qrels_dict[q] = new_paralist
    qrels_file.close()
    return qrels_dict

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
            if max_score>0.0:
                for p in q_dict.keys():
                    curr_score = rankings.get(q)[p]
                    rankings.get(q)[p] = curr_score/max_score
            else:
                for p in q_dict.keys():
                    rankings.get(q)[p] = 0.0
        runfiles[fname] = rankings
        f.close()
    print ("runfiles are read")
    return runfiles

def calculate_fet_scores(runfiles, features):
    fet_file_dict = {}
    fetq = set()
    for rf in runfiles.keys():
        rfdata = runfiles.get(rf)
        for rfq in rfdata.keys():
            for rfq_para in rfdata.get(rfq).keys():
                fetq.add(rfq+"_"+rfq_para)
    for qp in fetq:
        '''
        if qp == "enwiki:Ion:1f2a8ec61d05addf1d33b89555db46f6c78926fc_09a0215d88f8525232ec8e5480f5f77095ced7f4":
            print("this is it")
        '''
        
        query = qp.split('_')[0]
        para = qp.split('_')[1]
        fet_scores = []
        for fet in features:
            score = 0.0
            if query in runfiles.get(fet).keys() and para in runfiles.get(fet).get(query).keys():
                score = runfiles.get(fet).get(query).get(para)
            fet_scores.append(score)
        fet_file_dict[qp] = fet_scores
    print ("fet file scores are read")
    return fet_file_dict

def write_fet_file(fet_file_dict, qrels_dict, full_qrels_dict, out_fet_file):
    test_fold_fet_query = set()
    for fet_query in fet_file_dict.keys():
        scores = fet_file_dict.get(fet_query)
        query = fet_query.split('_')[0]
        para = fet_query.split('_')[1]
        qrelsq = fet_query.replace("_"," 0 ")
        if not query in qrels_dict.keys():
            if query in full_qrels_dict.keys():
                test_fold_fet_query.add(fet_query)
            continue
        if para in qrels_dict.get(query):
            fetline = "1"
        else:
            fetline = "0"
        for fet_count in range(len(scores)):
            fetline = fetline+" "+str(fet_count+1)+":"+str(scores[fet_count])
        #for debug mode
        fetline = fetline+" #"+fet_query
        #fetline = fetline+" #"+para
        with open(out_fet_file, "a+") as fetf:
            fetf.write(fetline+"\n")
    print ("fet file is written")
    return test_fold_fet_query
   
qrels_dir = sys.argv[1]
run_dir = sys.argv[2]
test_fold = sys.argv[3]
rlib_dir = sys.argv[4]
qrels_suffix = sys.argv[5]
out_dir = sys.argv[6]
#mode = sys.argv[7]
qrels = qrels_dir+"/"+qrels_suffix
test_runs_dir = ""

createFolder(out_dir)
createFolder(out_dir+"/fet-files")
createFolder(out_dir+"/models")
createFolder(out_dir+"/out-runs")

out_fet_file = ""
model_file = ""
out_test_run_file = ""

if test_fold.startswith("fold"):
    test_fold_no = test_fold[4:5]
    out_fet_file = out_dir+"/fet-files/"+test_fold+"-train-fet"
    model_file = out_dir+"/models/"+test_fold+"-train-model"
    out_test_run_file = out_dir+"/out-runs/comb-train-"+test_fold+"-run"
elif test_fold == "test":
    test_fold_no = "-1"
    out_fet_file = out_dir+"/fet-files/all-train-fet"
    model_file = out_dir+"/models/all-train-model"
    out_test_run_file = out_dir+"/out-runs/comb-test-run"
    test_runs_dir = sys.argv[7]
else:
    print ("not a valid fold!")
    sys.exit()

qrels_dict = read_qrels(qrels_dir, qrels_suffix, test_fold_no)
full_qrels_dict = read_qrels_full(qrels_dir, qrels_suffix)

runfiles = read_runs(run_dir)

features = sorted(os.listdir(run_dir))
fet_file_dict = calculate_fet_scores(runfiles, features)

print ("writing feature file");

test_fold_fet_query = write_fet_file(fet_file_dict, qrels_dict, full_qrels_dict, out_fet_file)

print ("handing over to Ranklib")

#java -jar /home/sumanta/Softwares/RankLib-2.1-patched.jar -train all-comb-rlib-fet -ranker 4 -metric2t MAP -save all-comb-rlib-fet-model
rlib = rlib_dir+"/RankLib-2.1-patched.jar"
subprocess.call(['java','-Xmx100g','-jar',rlib,'-train',out_fet_file,'-ranker','4','-metric2t','MAP','-save',model_file])

opt_weights = []
model = open(model_file,'r')
for line in model:
    if not line.startswith("#"): 
        weights = line.split()
        for i in range(len(weights)):
            opt_weights.append(weights[i].split(':')[1])

#enwiki:Carbohydrate/Metabolism Q0 4b5761ece8c97decb283f9a8eb5a88a1b62f3283 0 2.0 BOOL-MAP
if test_fold.startswith("fold"):
    with open(out_test_run_file, "a") as outrun:
        for test_q in test_fold_fet_query:
            scores = fet_file_dict.get(test_q)
            query = test_q.split('_')[0]
            para = test_q.split('_')[1]
            ret_score = 0
            for fet_count in range(len(scores)):
                ret_score = ret_score+float(scores[fet_count])*float(opt_weights[fet_count])
            outrun.write(query+" Q0 "+para+" 0 "+str(ret_score)+" COMB"+test_fold+"\n")
    print ("runfile written")
else:
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
                outrun.write(q+" Q0 "+p+" 0 "+str(ret_score)+" COMB"+test_fold+"\n")
    print ("runfile written")
            