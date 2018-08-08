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
        
qrels_dir = sys.argv[1]
run_dir = sys.argv[2]
test_fold = sys.argv[3]
rlib_dir = sys.argv[4]
qrels_suffix = sys.argv[5]
out_dir = sys.argv[6]
qrels = qrels_dir+"/"+qrels_suffix
test_runs_dir = ""

createFolder(out_dir)
createFolder(out_dir+"/fet-files")
createFolder(out_dir+"/models")
createFolder(out_dir+"/out-runs")

out_fet_file = ""
model_file = ""
out_test_run_file = ""
qrels_dict = {}

if test_fold.startswith("fold"):
    test_fold_no = test_fold[4:5]
    out_fet_file = "fet-files/"+test_fold+"-train-fet"
    model_file = "models/"+test_fold+"-train-model"
    out_test_run_file = "out-runs/comb-train-"+test_fold+"-run"
elif test_fold == "test":
    test_fold_no = "-1"
    out_fet_file = "fet-files/all-train-fet"
    model_file = "models/all-train-model"
    out_test_run_file = "out-runs/comb-test-run"
    test_runs_dir = sys.argv[7]
else:
    print ("not a valid fold!")
    sys.exit()

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

fetq = set()

runfiles = {}
features = sorted(os.listdir(run_dir))
for fname in features:
    scores = {}
    f = open(run_dir+"/"+fname)
    line = f.readline()
    while line:
        line_elems = line.split()
        runq = line_elems[0]+"_"+line_elems[2]
        runscore = line_elems[4]
        scores[runq] = runscore
        line = f.readline()
    runfiles[fname] = scores
    f.close()
print ("runfiles are read");

fet_file_dict = {}
for rf in runfiles.keys():
    rfdata = runfiles.get(rf)
    for rfkey in rfdata.keys():
        fetq.add(rfkey)

for qp in fetq:
    fet_scores = []
    for fet in features:
        score = 0
        if qp in runfiles.get(fet).keys():
            score = runfiles.get(fet).get(qp)
        fet_scores.append(score)
    fet_file_dict[qp] = fet_scores
print ("fet file scores are read")
print ("writing feature file");

test_fold_fet_query = set()
for fet_query in fet_file_dict.keys():
    scores = fet_file_dict.get(fet_query)
    query = fet_query.split('_')[0]
    para = fet_query.split('_')[1]
    qrelsq = fet_query.replace("_"," 0 ")
    if not query in qrels_dict.keys():
        test_fold_fet_query.add(fet_query)
        continue
    if para in qrels_dict.get(query):
        fetline = "1"
    else:
        fetline = "0"
    for fet_count in range(len(scores)):
        fetline = fetline+" "+str(fet_count+1)+":"+str(scores[fet_count])
    
    #for debug mode
    #fetline = fetline+" #"+fet_query
    fetline = fetline+" #"+para
    
    with open(out_fet_file, "a") as fetf:
        fetf.write(fetline+"\n")
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
    
            