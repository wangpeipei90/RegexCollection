# -*- coding: utf-8 -*-
### automatic the instrumentation process by taking advantage of maven options and configurations
### this file manipulate three directories: soot, reop, and target
import os
import sys
import subprocess
import shutil

pthreads=4
sep=":" ##seperator is only comma in Unix/Linux
instrument_dir="/home/peipei/RepoReaper/soot_instrument"
instrument_jars="/home/peipei/RepoReaper/soot_instrument/*"
#instrument_class="edu.ncsu.se.regex.PatternInstrument2"
instrument_class="edu.ncsu.se.regex.PatternInstrument3"
java_cp="/opt/jdk1.7.0_80/jre/lib/rt.jar:/opt/jdk1.7.0_80/jre/lib/jce.jar" ##default 

##compose a settings.xml  
#<?xml version="1.0" encoding="UTF-8"?>
#<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
#          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
#  <localRepository>${proj_path}/repo</localRepository>
#</settings>
def compose(proj_path):
    proj_path=proj_path.rstrip('/')  ##remove trailing slashes
    
    file_path=proj_path+"/settings.xml"
    repo_path=proj_path+"/repo"
    repo_path_absolute=os.path.realpath(repo_path)  
    print "repo path ", repo_path
    print "repo path absolute: ", repo_path_absolute
    xml_repo=open(file_path,"w") 
    xml_repo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    xml_repo.write('<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"\n')
    xml_repo.write('          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    xml_repo.write('          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">\n')
    xml_repo.write('  <localRepository>'+repo_path_absolute+'</localRepository>\n')
    xml_repo.write('</settings>\n')
    xml_repo.close()
##end of compose(proj_path)

def check_pom(proj_path):
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
##end of check_pom(proj_path) 
###mvn -Dmaven.artifact.thread=${pthreads} --settings ./settings.xml test
##requires to change directory
def mvn_test(proj_path):
    cur_cwd=os.getcwd()
    print "cur cwd: ",cur_cwd 

    proj_path=proj_path.rstrip('/')
    
    print "start mvn original compile and test"
    os.chdir(proj_path)
    print "change directory to ", proj_path
    
    p_mvn_test=subprocess.Popen(["mvn","-Dmaven.artifact.thread="+str(pthreads),"--settings","./settings.xml","test"],stdout=subprocess.PIPE)
 #   print "mvn test sys stdout"
 #   for line in iter(p_mvn_test.stdout.readline, ''):
	#sys.stdout.write(line)
    output,err=p_mvn_test.communicate()
    output_mvn_test=output.strip()
    ret=p_mvn_test.wait()
    p_mvn_test.stdout.close()
    
    print "mvn test output:",output_mvn_test
    print "mvn test error:",err
    print "mvn test ret code:",ret
    
    os.chdir(cur_cwd)
    print "change directory back to original work dir", cur_cwd
    
    return ret
##end of mvn_test(proj_path)

##extract all jars in repository and this will be relied on during soot Instrumentation
##lib_jars=`find repo -name "*.jar"|sort -r|paste -sd':'`
def extractJars(proj_path):
    proj_path=proj_path.rstrip('/')
    repo_path=proj_path+"/repo"    
    
    p_find=subprocess.Popen(["find",repo_path,"-name","*.jar"],stdout=subprocess.PIPE)
    p_sort=subprocess.Popen(["sort","-r"],stdin=p_find.stdout,stdout=subprocess.PIPE) ##sort reverse so that latest jars are first
    p_paste=subprocess.Popen(["paste","-sd:"],stdin=p_sort.stdout,stdout=subprocess.PIPE)
    
    output_paste,err_paste=p_paste.communicate()
    p_paste.stdout.close()
    
    if err_paste>0:
        return None
    else:
        return output_paste.strip()
##end of extractJars


##reqires lib_jars, instrument_file, instrument_jar target/test-classes target/classes 
##java -cp $lib_jars:$instrument_file|jar:target/test-classes|classes PatternInstrument2 
##-cp /opt/jdk1.7.0_80/jre/lib/rt.jar -process-dir target/classes|test-classes -output-dir soot/classes|test-classes

def instrument(proj_path,log_file):
    lib_jars=extractJars(proj_path)
    print "lib jars: ", lib_jars
 
    cur_cwd=os.getcwd()  
    print "cur cwd: ",cur_cwd,"proj path: ",proj_path
    print "start instrument"
    os.chdir(proj_path)
    print "change directory to ", proj_path
    
    
    ##instrument classes dirs relative to target/soot
    dirs=["classes","test-classes"]
    
    ##compose classpath
    paths=[instrument_dir,instrument_jars,lib_jars]
    for class_dir in dirs:
        paths.append("target/"+class_dir)
    paths.append("/opt/jdk1.7.0_80/jre/lib/jce.jar")

    soot_cp=':'.join(paths)
    
    print "soot classpath",soot_cp
    
    ##run instrument    
    for class_dir in dirs:
        p_instrument=subprocess.Popen(["/opt/jdk1.7.0_80/bin/java","-cp",soot_cp,instrument_class,log_file,"-cp",java_cp,"-f","class",
            "-process-dir","target/"+class_dir,"-output-dir","soot/"+class_dir],stdout=subprocess.PIPE)
        
        #p_instrument=subprocess.Popen(["/opt/jdk1.7.0_80/bin/java","-cp",soot_cp,instrument_class,"-cp",java_cp,"-f","dava",
        #    "-process-dir","target/"+class_dir,"-output-dir","soot2/"+class_dir],stdout=subprocess.PIPE)
        output_instrument,err_instrument=p_instrument.communicate()
        output_instrument=output_instrument.strip()
        print "auto soot instrument output:",output_instrument
	print "auto soot instrument error:",err_instrument
	print "auto soot instrument ret code:", p_instrument.wait()
	p_instrument.stdout.close()
    
    os.chdir(cur_cwd)
    print "change directory back to original work dir", cur_cwd
##end of instrument(proj_path)

def runLinuxCommand(args):  ##list of arguments
    p_cmd=subprocess.Popen(args,stdout=subprocess.PIPE)
    output,err=p_cmd.communicate()
    output=output.strip()
    ret=p_cmd.wait()
    p_cmd.stdout.close()
    
    if ret>0:
        sys.stderr.write("failure in "+args)
	sys.stderr.write("\n")
        sys.exit()
#end of def runLinuxCommand


##replace target with soot, and run mvn surefire:test  
##no other lifecycle phase will be executed(compile) only test
def soot_test(proj_path):
    cur_cwd=os.getcwd()
    proj_path=proj_path.rstrip('/')
    print "cur cwd: ",cur_cwd, "proj path: ", proj_path 
    print "start mvn surefire:test after instrument"
    os.chdir(proj_path)
    print "change directory to ", proj_path
    
    
    ##copy soot to "target", we need to keep the resource files
    runLinuxCommand(["rm","-rf","target/classes"])
    runLinuxCommand(["rm","-rf","target/test-classes"])
    runLinuxCommand(["cp","-rf","soot/classes","target"])
    runLinuxCommand(["cp","-rf","soot/test-classes","target"])

    ##shutil.rmtree('soot')###we should keep the soot for debugging purpose

    ##run mvn  surefire:test  -o,--offline:              Work offline
    p_soot_test=subprocess.Popen(["mvn","-o","-Dmaven.artifact.thread="+str(pthreads),"--settings","./settings.xml","surefire:test"],stdout=subprocess.PIPE)
 #   print "mvn test sys stdout"
 #   for line in iter(p_mvn_test.stdout.readline, ''):
	#sys.stdout.write(line)
    output,err=p_soot_test.communicate()
    output_soot_test=output.strip()
    ret=p_soot_test.wait()
    p_soot_test.stdout.close()
    
    print "mvn test output:",output_soot_test
    print "mvn test error:",err
    print "mvn test ret code:",ret
    
    ##if soot test succeeds, save results to file
    res=open("res.txt",'w')
    res.write(output_soot_test)
    
    os.chdir(cur_cwd)
    print "change directory back to original work dir", cur_cwd
    
    return ret
##end of soot_test(proj_path)


def process(proj_path,log_file):
    proj_path=proj_path.rstrip('/')  ##remove trailing slashes
    proj_path=os.path.abspath(proj_path)

    compose(proj_path)
    res=mvn_test(proj_path)
    #if res>0:
    #    print "error in mvn test"
    instrument(proj_path,log_file)
    sys.exit(0)
    soot_test(proj_path)
    
if __name__ == "__main__":
   if len(sys.argv)<2:
	print "This process need a directory to process as argument!!"
	sys.exit(1)
   else:
	proc_dir=sys.argv[1]
	log_file=sys.argv[2]
	process(proc_dir,log_file)
