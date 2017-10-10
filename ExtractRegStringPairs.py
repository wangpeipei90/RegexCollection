import os
import re
import pickle
import csv
file_name = "/home/peipei/RepoReaper/results" #file to be searched
cur_dir = os.getcwd() # Dir from where search starts can be replaced with any path

reg_str={}

f = open(file_name, "r")
lines = f.readlines()
for line in lines:
    output=line.strip()
    print output
    
    f2=open(cur_dir+output,"r")
    lines2=f2.readlines()
    reg_s=None
    str_s=None
    for line2 in lines2:
        line2=line2.strip()
        if line2.startswith("Pattern: "):
                reg_s=line2[9:]
                if reg_s not in reg_str:
                    reg_str[reg_s]=set()
        elif line2.startswith("String: "):
                str_s=line2[8:]
                reg_str[reg_s].add(str_s)
                str_s=None
                reg_s=None
    
    output = open('reg_str', 'wb+')
    pickle.dump(reg_str, output)
    output.close()

    with open('reg_str.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in reg_str.items():
            writer.writerow([key, value])
    ## read data
    output = open('reg_str', 'rb')
    obj_dict = pickle.load(output)   
    for key, value in reg_str.items():
            print(key)
    #file_list = os.listdir(cur_dir)
    #parent_dir = os.path.dirname(cur_dir)
    #if file_name in file_list:
    #    print "File Exists in: ", cur_dir
    #    ##read file
    #    
    #    break
    #else:
    #    if cur_dir == parent_dir: #if dir is root dir
    #        print "File not found"
    #        break
    #    else:
    #        cur_dir = parent_dir