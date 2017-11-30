import re
import sys
import os
import codecs
import pickle

stack_trace=r'^Stack Trace from: (.*) in class: (.*)\[on line number: (-?[0-9]+) of file: (.*).java\]'
pattern_full=r'^Pattern matches\(String regex, CharSequence input\)---regex: (.*)---input: (.*)'''
matcher_full=r'^Matcher matches\(\)---regex: (.*)---input: (.*)'''
ws="/home/peipei/RepoReaper/logs"

stack_regex=re.compile(stack_trace)
pattern_regex=re.compile(pattern_full)
matcher_regex=re.compile(matcher_full)

def check(i):
    '''Test if logs exists and regex not exist'''
    is_log=os.path.isfile(str(i)+".log")
    is_regex=os.path.isfile(str(i)+".regex")
    
    is_needed=is_log and (not is_regex)
    return is_needed
    
def process_proj(proj):
    need_process=check(proj)
    if not need_process:
        return 0
    print "project: ",str(proj)
    f = codecs.open(str(proj)+".log", 'r',encoding='utf-8')
    dict_regex=dict()

    print "before parsing"
    trace=list()
    i=0
    for line in f:
        i+=1
	if line=='':
            continue
	print "line: ", line
	m1=stack_regex.match(line)
	if m1 is not None:
	    method_str=m1.group(1)
	    class_str=m1.group(2)
	    line_str=m1.group(3)
	    file_str=m1.group(4)
	    strace=(file_str,line_str,class_str,method_str)
	    trace.append(strace)
	    print "match stack trace: ",strace
	    continue

	print "stacktrace: ", trace
	#not stack trace, it is regex and string	
        m1=pattern_regex.match(line)
        if m1 is None:
            m1=matcher_regex.match(line)
	    isMatcherMatch=True
        if m1 is not None:
	    print "Matcher match" if isMatcherMatch else "Pattern match"

            regex_str=m1.group(1)
            input_str=m1.group(2)
            print i, repr(regex_str), repr(input_str), trace
            
        if regex_str not in dict_regex:
            dict_regex[regex_str]=dict() ##map structure: make it unique
	dict_regex[regex_str][input_str]=trace
	trace=[]

    f.close()
    print("finish picking regex")
    if len(dict_regex)>0:
        print("dump regex: ")
        print(str(proj)+".regex")
        #output=codecs.open(str(proj)+".regex",'w',encoding='utf8')
        output=open(str(proj)+".regex",'w')
        pickle.dump(dict_regex, output)
        output.close() 
        print("dump regex")      
        #read it back
        #handle=open('7.regex','r')
        #b=pickle.loads(handle.read())

        
        

if __name__== '__main__':
	if sys.argv is None or len(sys.argv)<2: #[begin,end)
		sys.exit('Error! You need to specify one project ID or both begin and end project ID!!')
	begin=int(sys.argv[1])
	end=begin
	if len(sys.argv)==3:
		end=int(sys.argv[2])
	elif len(sys.argv)==2:
		end=begin+1
	print begin, end
	os.chdir(ws)
	for i in range(begin,end):
	   process_proj(i)

