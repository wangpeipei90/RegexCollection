import re
import os
import subprocess
import shutil
import sys
wfile = open("JavaValidProjectIDs.txt","w") 
with open("JavaProjectsWithUnitTest5.txt") as rfile:
    i=0
    for line in rfile:
        i+=1 ##i is the download directory
	if i<792:
		continue
	if i>2000:
		break
	line=line.strip()

        #items=re.split(r'\t+',line) ##page,row, proj,unit, api,v_api, url, v_url
        #string_url=items[7]
	#validation_url=times[6]

        items=re.split(r'\t+',line) ##page,row, proj, unit, community, continous integrity, documentation, history, issues, license, size, state, stars, timestamp, api,v_api, url, v_url
	print(items)

        name_proj=items[2]
        unit=items[3]
        string_url=items[17]
	validation_url=items[18]

#	print(validation_url)
#	if int(validation_url)<1:  ## if the url is not valid we could not download
#		print("not valid url")
       
	if int(validation_url)<1:  ## if the url is not valid we could not download
		continue 

        cmd_git="git clone "+string_url+".git "+str(i)
	print cmd_git

        status_git=os.system(cmd_git)
	print status_git

#        if status_git>0:  ## if the ith directory exists, this repository must have been cloned and searched already.
#            continue


	print "start mvn processing"

	###filter for mvn
	os.chdir(str(i))
	print "change directory to ", str(i)

	##find . (-maxdepth 3) -name "pom.xml" -printf "%d %h\n" ##depth directories
	#p_pom=subprocess.Popen(["find",".","-name","pom.xml","-printf","%d %h\n"],stdout=subprocess.PIPE)
	p_pom=subprocess.Popen(["find",".","-name","pom.xml"],stdout=subprocess.PIPE)
	p_pom_xml=subprocess.Popen(["wc","-l"],stdin=p_pom.stdout,stdout=subprocess.PIPE) ##example of piped command line find|wc 
	p_pom.stdout.close()

	output_xml,err_xml=p_pom_xml.communicate()
	output_xml=output_xml.strip()
	print "pom.xml output:",output_xml
	print "pom.xml error:",err_xml
	print "pom.xml ret code:", p_pom_xml.wait()
	p_pom_xml.stdout.close()

        if err_xml!=None or int(output_xml)==0: ##error or no found code
	     print("no maven pom.xml or grep error")



        pom_depth=0
	pom_need=0
	pom_error=0
        test_error=0 
	if int(output_xml)>0:   ##first select the ones having pom.xml
	#if False:
		p_pom2=subprocess.Popen(["find",".","-name","pom.xml","-printf","%d:%h\n"],stdout=subprocess.PIPE)
		p_pom_sort=subprocess.Popen(["sort","-n"],stdin=p_pom2.stdout,stdout=subprocess.PIPE) ##example of piped command line find|sort by depth
		p_pom2.stdout.close()

		output_sort,err_sort=p_pom_sort.communicate()
#		output_sorts=output_sort.strip().split()
#		output_sorts2=output_sort.split("\n")
		output_sorts=re.split(":|\n",output_sort.strip())
		print "pom sort output:",output_sort
		print "pom sort output strip:",output_sorts
#		print "pom sort output strip:",output_sorts2
#		print "pom sort output strip:",output_sorts3
		print "pom sort error:",err_sort
		print "pom sort ret code:", p_pom_sort.wait()
		p_pom_sort.stdout.close()


		min_depth=output_sorts[0]
		f_dir=output_sorts[1]

		pom_depth=int(min_depth)

		if f_dir==".":
			pom_need=1

			p_mvn_compile=subprocess.Popen(["mvn","compile"],stdout=subprocess.PIPE)
			print "mvn compile sys stdout"
			for line in iter(p_mvn_compile.stdout.readline, ''):
				sys.stdout.write(line)

			output,err=p_mvn_compile.communicate()
			output_mvn_compile=output.strip()
			ret=p_mvn_compile.wait()
			p_mvn_compile.stdout.close()
			print "mvn compile output:",output_mvn_compile
			print "mvn compile error:",err
			print "mvn compile ret code:",ret

			if ret>0:
				pom_error+=1
			else: ##if compile successfully
				p_mvn_test=subprocess.Popen(["mvn","test"],stdout=subprocess.PIPE)
				print "mvn test sys stdout"
				for line in iter(p_mvn_test.stdout.readline, ''):
					sys.stdout.write(line)

				output,err=p_mvn_test.communicate()
				output_mvn_test=output.strip()
				ret=p_mvn_test.wait()
				p_mvn_test.stdout.close()
				print "mvn test output:",output_mvn_test
				print "mvn test error:",err
				print "mvn test ret code:",ret
				
				if ret>0:
					test_error+=1
				
		else:	
			dirs=0
			while dirs<int(output_xml):
				cur_depth=output_sorts[2*dirs]

				if cur_depth==min_depth:
					pom_need+=1

					cur_dir=output_sorts[2*dirs+1]

					cur_cwd=os.getcwd()
					os.chdir(cur_dir)
					print "change directory to ", str(i), "/", cur_dir

					p_mvn_compile=subprocess.Popen(["mvn","compile"],stdout=subprocess.PIPE)
					output,err=p_mvn_compile.communicate()
					output_mvn_compile=output.strip()
					ret=p_mvn_compile.wait()
					p_mvn_compile.stdout.close()
					print "mvn compile output:",output_mvn_compile
					print "mvn compile error:",err
					print "mvn compile ret code:",ret 

					if ret>0:
						pom_error+=1

					else:
						p_mvn_test=subprocess.Popen(["mvn","test"],stdout=subprocess.PIPE)
						output,err=p_mvn_test.communicate()
						output_mvn_test=output.strip()
						ret=p_mvn_test.wait()
						p_mvn_test.stdout.close()
						print "mvn test output:",output_mvn_test
						print "mvn test error:",err
						print "mvn test ret code:",ret
						
						if ret>0:
							test_error+=1
					os.chdir(cur_cwd)
					print "change directory back to ", cur_cwd
					
					dirs+=1
				else:
					break
			
		
	os.chdir("..")
	print "change directory back to previous of ", str(i)
	

        ##after download, search for import java.util.regex.*, 
        #import java.util.regex.Matcher, import java.util.regex.Pattern
#        m1=r'import java.util.regex.*' ##in m1 star is used as regular expression character
#        m2=r'import java.util.regex.Matcher' ##m1 could match m2 and match m3
#        m3=r'import java.util.regex.Pattern' ##thus do not need m2 and m3
	#some may only directly use java.util.regex and do not import them
	m=r'java.util.regex.*'

#       cmd_grep="grep -nr \""+m+"\" "+str(i)
#	print cmd_grep
#       status_grep=os.system(cmd_grep)
#	print status_grep

	p1=subprocess.Popen(["grep","-nr",m,str(i)],stdout=subprocess.PIPE)
	p2=subprocess.Popen(["wc","-l"],stdin=p1.stdout,stdout=subprocess.PIPE) ##example of piped command line
	p1.stdout.close()
	output,err=p2.communicate()
	output_regex=output.strip()
	print "java.util.regex output:",output
	print "java.util.regex error:",err
	print "java.util.regex ret code:", p2.wait()

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

        if err!=None or int(output_regex)==0: ##error or no found code
	     print("no java.util.regex.* is used or grep error")
#            os.system("rm -rf"+str(i)) #remove dir
#	     shutil.rmtree(str(i),ignore_errors=False,onerror=None) ## since there are string matches regex, should not remove dir

	if int(output_xml)==0:
	     shutil.rmtree(str(i),ignore_errors=False,onerror=None) ## since no pom.xml we do not spend time on it
        else:
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

_name__== '__main__':
	if sys.argv is None or len(sys.argv)<3: (begin,end]
		sys.exit('Error! You need to specify begin and end project ID!!')
	ws="/home/peipei/RepoReaper/" ##workspace
	begin=argv[1]
	end=argv[2]
