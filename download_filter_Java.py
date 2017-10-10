import re
import os
import subprocess
import shutil
wfile = open("JavaValidProjectIDs.txt","w") 
with open("JavaProjectsWithUnitTest3.txt") as rfile:
    i=0
    for line in rfile:
        i+=1 ##i is the download directory
#	if i>4:
#		break
	line=line.strip()

        items=re.split(r'\t+',line) ##page,row, proj,unit, api,v_api, url, v_url
        name_proj=items[0]
        unit=items[1]
        string_url=items[3]
        
        cmd_git="git clone "+string_url+".git "+str(i)
	print cmd_git
        status_git=os.system(cmd_git)
	print status_git
        if status_git>0:
            continue
        ##after download, search for import java.util.regex.*, 
        #import java.util.regex.Matcher, import java.util.regex.Pattern
#        m1=r'import java.util.regex.*' ##in m1 star is used as regular expression character
#        m2=r'import java.util.regex.Matcher' ##m1 could match m2 and match m3
#        m3=r'import java.util.regex.Pattern' ##thus do not need m2 and m3
        
	#some may only directly use java.util.regex and do not import them
	m=r'java.util.regex.*'

#        cmd_grep="grep -nr \""+m+"\" "+str(i)
#	print cmd_grep
#        status_grep=os.system(cmd_grep)
#	print status_grep

	p1=subprocess.Popen(["grep","-nr",m,str(i)],stdout=subprocess.PIPE)
	p2=subprocess.Popen(["wc","-l"],stdin=p1.stdout,stdout=subprocess.PIPE)
	p1.stdout.close()
	output,err=p2.communicate()
	output=output.strip()
	print "output:",output
	print "error:",err
	print "ret code:", p2.wait()

	#cmd_grep2=cmd_grep+"|wc -l"
	#print cmd_grep2
        #status_grep2=os.system(cmd_grep2)
	#print status_grep2
	
	#res=subprocess.getoutput(cmd_grep2)
	#print res

	#p=subprocess.Popen(cmd_grep2,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#occur=p.stdout.read()
	#ret_grep2=p.wait()
	#print occur
	#print ret_grep2

        if err!=None or int(output)==0: ##error or no found code
#            os.system("rm -rf"+str(i)) #remove dir
	     shutil.rmtree(str(i),ignore_errors=False,onerror=None)
        else:
            wfile.write(str(i))
            wfile.write("\t")
            wfile.write(str(output))
            wfile.write("\n")
	    wfile.flush()

wfile.close()
