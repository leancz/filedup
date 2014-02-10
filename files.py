import os
import sys
from collections import defaultdict
import filecmp

def file_list(dir):
    return [f for f in os.listdir(dir)]

fileList = defaultdict(list)
rootdir = sys.argv[1]

for root, subFolders, files in os.walk(rootdir):
    for file in files:
        f = os.path.join(root,file)
        file_size = os.path.getsize(f)
        #print(f)
        fileList[file_size].append(f)

for i in fileList:
    if len(fileList[i])>2:
        print "More than two possibles", i, fileList[i]
    if len(fileList[i])==2:
        if filecmp.cmp(fileList[i][0], fileList[i][1]):
            print "THE SAME ... APPARENTLY", i, fileList[i]





