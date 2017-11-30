import re
import os
import subprocess
import shutil
import sys
import logging
from edit_pom import agent_pom

proj_list="/home/peipei/RepoReaper/RegexCollection/JavaProjectsWithUnitTest.txt"
log_path="/home/peipei/RepoReaper/loggings/"
ws="/home/peipei/RepoReaper/" ##workspace

def createLog(filename):
    print("log------------------------")
    log = logging.getLogger(filename)
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
                fmt='%(asctime)s %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
                )
    fh.setFormatter(formatter)
    log.addHandler(fh)
    print("log------------------------")
    return log,fh
def closeLog(log,fh):
    log.removeHandler(fh)
    del fh,log
def download(i,line,log,fh):
    #items=re.split(r'\t+',line) ##page,row, proj,unit, api,v_api, url, v_url
    #string_url=items[7]
        #validation_url=times[6]
    items=re.split(r'\t+',line) ##page,row, proj, unit, community, continous integrity, documentation, history, issues, license, size, state, stars, timestamp, api,v_api, url, v_url
    log.info("items: %s" % items)
    print "items: ",items

    #name_proj=items[2]
    #unit=items[3]
    string_url=items[17]
    validation_url=items[18]

    #	print(validation_url)
    #	if int(validation_url)<1:  ## if the url is not valid we could not download
    #	print("not valid url")

    if int(validation_url)<1:  ## if the url is not valid we could not download
        log.error("url is not valid for download")
        closeLog(log,fh)
        return 1

    ##add username:password for https://github.com
    string_url="https://wangpeipei90:jiangzhen123456@"+string_url[8:]
    cmd_git="git clone "+string_url+".git "+str(i)
    log.info(cmd_git)

    status_git=os.system(cmd_git)
    log.info("git status: "+str(status_git))
    print "git status: "+str(status_git)

#    if status_git==32768:
#	return 1

    if os.path.exists(ws+str(i)) and status_git>0:
        log.info("the project has already existed.")
        print "the project has already existed."
    elif status_git>0:
	return 1

    return 0
def calPom(log,fh):
    ##find . (-maxdepth 3) -name "pom.xml" -printf "%d %h\n" ##depth directories
    #p_pom=subprocess.Popen(["find",".","-name","pom.xml","-printf","%d %h\n"],stdout=subprocess.PIPE)
    p_pom=subprocess.Popen(["find",".","-name","pom.xml"],stdout=subprocess.PIPE)
    p_pom_xml=subprocess.Popen(["wc","-l"],stdin=p_pom.stdout,stdout=subprocess.PIPE) ##example of piped command line find|wc

    p_pom.stdout.close()
    p_pom.wait()
    output_xml,err_xml=p_pom_xml.communicate()
#    p_pom_xml.stdout.close()
#    p_pom_xml.wait()

    output_xml=output_xml.strip()
    log.info("pom.xml output| total number of pom.xml: %s" % output_xml)
    log.error("pom.xml error: %s" % err_xml)
    log.info("pom.xml ret code: %d" % p_pom_xml.returncode)
    return output_xml,err_xml

def sortPom(log,fh):
    p_pom2=subprocess.Popen(["find",".","-name","pom.xml","-printf","%d:%h\n"],stdout=subprocess.PIPE)
    p_pom_sort=subprocess.Popen(["sort","-n"],stdin=p_pom2.stdout,stdout=subprocess.PIPE) ##example of piped command line find|sort by depth
    p_pom2.stdout.close()
    p_pom2.wait()

    output_sort,err_sort=p_pom_sort.communicate()
#    p_pom_sort.stdout.close()
#    p_pom_sort.wait()

    #output_sorts=output_sort.strip().split()
    #output_sorts2=output_sort.split("\n")
    output_sorts=re.split(":|\n",output_sort.strip())
    log.info("pom sort output: %s" % output_sort)
    log.info("pom sort output strip: %s" % output_sorts)
    #print "pom sort output strip:",output_sorts2
    #print "pom sort output strip:",output_sorts3
    log.info("pom sort error: %s" % err_sort)
    log.info("pom sort ret code: %d" % p_pom_sort.returncode)

    return output_sorts,err_sort;

def mvn_compile(i,f_dir,dep,log,fh):
    log.info("find pom.xml in depth: "+dep+" at the project directory: "+f_dir)
    print("mvn compile find pom.xml in depth: "+dep+" at the project directory: "+f_dir)
    p_mvn_compile=subprocess.Popen(["mvn","compile"],stdout=subprocess.PIPE)
    output,err=p_mvn_compile.communicate()
#    p_mvn_compile.stdout.close()
#    ret=p_mvn_compile.wait()

    output_mvn_compile=output.strip()
    log.info("mvn compile output: %s" % output_mvn_compile)
    log.error("mvn compile error: %s" % err)
    log.info("mvn compile ret code:%d" % p_mvn_compile.returncode)

    ret=p_mvn_compile.returncode
    if ret>0:
        log.error("Error in original mvn compile under the current directory: %d",i)
        return 1
    return 0

def mvn_test(i,f_dir,dep,log,fh):
    print("now run mvn test")
    p_mvn_test=subprocess.Popen(["mvn","test"],stdout=subprocess.PIPE)
    #print "mvn test sys stdout"
    output,err=p_mvn_test.communicate()
#    p_mvn_test.stdout.close()
#    ret=p_mvn_test.wait()

    output_mvn_test=output.strip()
    log.info("mvn test output: %s" % output_mvn_test)
    log.error("mvn test error: %s" % err)
    log.info("mvn test ret code: %d" % p_mvn_test.returncode)



    ret=p_mvn_compile.returncode
    if ret>0:
        log.error("Error in original mvn test under the current directory: %d" %i)
        return 1
    return 0

def mvn_process(i,log,fh):
    log.info("start mvn processing")
    print("start mvn processing")
    os.chdir(ws+str(i))
    log.info("change directory to %s" % str(i))
    print "change directory to ", str(i)

    output_xml,err_xml=calPom(log,fh)
    if err_xml!=None or int(output_xml)==0: ##error or no found code
        os.chdir(ws)
	log.info("change directory back to parent of %s" % str(i))
        log.error("stop the process and delete the directory because no maven pom.xml")
        shutil.rmtree(str(i),ignore_errors=False,onerror=None) ## since no pom.xml we do not spend time on it
        
        return None

    output_sorts,err_sort=sortPom(log,fh)
    pom_need=0
    pom_error=0
    test_error=0
    min_depth=output_sorts[0]
    f_dir=output_sorts[1]
    #pom_depth=int(min_depth)



    if f_dir==".":
        pom_need=1
        comp_error=mvn_compile(i,f_dir,min_depth,log,fh)
        if comp_error:
            pom_error+=1
	else:
            t_error=mvn_test(i,f_dir,min_depth,log,fh)
            if t_error:
                test_error+=1
            log.info("change pom.xml")
            print("change pom.xml")
            agent_pom(ws+str(i)+"/pom.xml",str(i))
            log.info("run mvn test on changed pom.xml")
            print("run mvn test on changed pom.xml")
            t_error=mvn_test(i,f_dir,min_depth,log,fh)
    else:
        dirs=0
        while dirs<int(output_xml): ##even is depth and odd is dirpath
		cur_depth=output_sorts[2*dirs]  ##min_depth could be start to be 2 and have parallel sub projects
		if cur_depth==min_depth:
			pom_need+=1
			cur_dir=output_sorts[2*dirs+1]
			cur_cwd=os.getcwd()
			os.chdir(cur_dir)
			log.info("change directory to %s" % str(i)+"/"+cur_dir)
                	comp_error=mvn_compile(i,f_dir,min_depth,log,fh)
			if comp_error:
				pom_error+=1
			else:
				t_error=mvn_test(i,cur_dir,cur_depth,log,fh)
				if t_error:
					test_error+=1
			    	log.info("change pom.xml")
				agent_pom(ws+str(i)+"/"+cur_dir+"/pom.xml",str(i))
				log.info("run mvn test on changed pom.xml")
				t_error=mvn_test(i,f_dir,min_depth,log,fh)
			os.chdir(cur_cwd)
    			log.info("change directory back to %s" % cur_cwd)
    			dirs+=1
		else:
			break
			
    return (output_xml,min_depth,pom_need,pom_error,test_error)


def calRegex(i,log,fh):
    ##after download, search for import java.util.regex.*,
    #import java.util.regex.Matcher, import java.util.regex.Pattern
    #m1=r'import java.util.regex.*' ##in m1 star is used as regular expression character
    #m2=r'import java.util.regex.Matcher' ##m1 could match m2 and match m3
    #m3=r'import java.util.regex.Pattern' ##thus do not need m2 and m3
    #some may only directly use java.util.regex and do not import them
	m=r'java.util.regex.*'

    #   cmd_grep="grep -nr \""+m+"\" "+str(i)
    #	print cmd_grep
    #   status_grep=os.system(cmd_grep)
    #	print status_grep

	p1=subprocess.Popen(["grep","-nr",m,str(i)],stdout=subprocess.PIPE)
	p2=subprocess.Popen(["wc","-l"],stdin=p1.stdout,stdout=subprocess.PIPE) ##example of piped command line
	p1.stdout.close()
	p1.wait()
	output,err=p2.communicate()
#	p2.stdout.close()
#	p2.wait()

	output_regex=output.strip()
	log.info("java.util.regex output: %s" % output)
	log.error("java.util.regex error: %s" % err)
	log.info("java.util.regex ret code: %d" % p2.returncode)

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
    	return (output_regex,err)

def writeToFile(i,output_xml,pom_depth,pom_need,pom_error,test_error,output_regex):
    wfile = open("RegexCollection/JavaValidProjectIDs.txt","w")
    wfile.write(str(i))
    wfile.write("\t")
    wfile.write(str(output_xml))
    wfile.write("\t")
    wfile.write(str(pom_depth))
    wfile.write("\t")
    wfile.write(str(pom_need))
    wfile.write("\t")
    wfile.write(str(pom_error))
    wfile.write("\t")
    wfile.write(str(test_error))
    wfile.write("\t")
    wfile.write(str(output_regex))
    wfile.write("\n")
    wfile.flush()

    wfile.close()

def download_instrument(begin,end): #(begin,end]
    print("1------------------------")
    with open(proj_list) as rfile:
    	print("2------------------------")
        i=0
        for line in rfile:
            i+=1 ##i is the download directory
       	    if i<=begin:
      		continue
       	    if i>end:
      		break
	    print("i: "+str(i))
            log,fh = createLog(log_path+str(i)+".log")
       	    line=line.strip()
            ret=download(i,line,log,fh)
	    if ret:
		print("not valid download")
		continue		

	    print("------------------------")
	    res=mvn_process(i,log,fh)
	    if res is None:
	        continue
	        
            output_xml,pom_depth,pom_need,pom_error,test_error=res
	    print("------------------------")

	    os.chdir(ws)
	    log.info("change directory back to previous of %s" % str(i))
            output_regex,err=calRegex(i,log,fh)
	    print("------------------------")
            if err!=None or int(output_regex)==0: ##error or no found code
                log.info("no java.util.regex.* is used or grep error")
                writeToFile(i,output_xml,pom_depth,pom_need,pom_error,test_error,0)
            else:
                writeToFile(i,output_xml,pom_depth,pom_need,pom_error,test_error,output_regex)
            closeLog(log,fh)

if __name__== '__main__':
	if sys.argv is None or len(sys.argv)<2: #(begin,end]
		sys.exit('Error! You need to specify one project ID or begin and end project ID!!')
	begin=int(sys.argv[1])
	end=begin
	if len(sys.argv)==3:
		end=int(sys.argv[2])
	elif len(sys.argv)==2:
		begin=begin-1
	print begin, end
	os.chdir(ws)
	download_instrument(begin,end)
