import re
import sys
import os
import codecs
import pickle
import itertools
#stack_trace=r'^Stack Trace from: (.*) in class: (.*)\[on line number: (-?[0-9]+) of file: (.*).java\]'
#pattern_full=r'^Pattern matches\(String regex, CharSequence input\)---regex: (.*)---input: (.*)'''
#matcher_full=r'^Matcher matches\(\)---regex: (.*)---input: (.*)'''
stack_trace=r'^Stack Trace from: (?P<method>.*) in class: (?P<class>.*)\[on line number: (?P<line>-?[0-9]+) of file: (?P<file>.*).java\]'
pattern_full=r'^Pattern matches\(String regex, CharSequence input\)---regex: (?P<regex>.*)---input: (?P<input>.*)'''
matcher_full=r'^Matcher matches\(\)---regex: (?P<regex>.*)---input: (?P<input>.*)'''
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

# def getFirstReflection(trace):
#     # mType=0
#     # if trace[1][3]=='Matcher' and trace[1][0]=='matches':
#     #     mType=2
#     # elif trace[1][3]=='Pattern' and trace[1][0]=='matches':
#     #     mType=1      
#     return 
    
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
	    method_str=m1.group('method')  ##matches
	    class_str=m1.group('class')
	    line_str=m1.group('line')
	    file_str=m1.group('file')  ##Matcher.java Pattern.java
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

            regex_str=m1.group('regex')
            input_str=m1.group('input')
            
            if regex_str not in dict_regex:
                dict_regex[regex_str]=dict() ##map structure: make it unique
            if input_str not in dict_regex[regex_str]:
                dict_regex[regex_str][input_str]=list()
                
            ###handle trace information
            simplified=tuple(itertools.takewhile(lambda e: e[3]!='invoke0' and e[2]!='sun.reflect.NativeMethodAccessorImpl' and e[1]!='-2' and e[0]!='NativeMethodAccessorImpl', trace[1:]))
	    print "trace: ", trace
	    print "simplified: ", simplified
            dict_regex[regex_str][input_str].append(simplified) ###tuple, list is not hashable
            trace=[]

            #print i, repr(regex_str), repr(input_str), trace
  #           output.write("{};{};{};".format(regex_str,input_str,isMatcherMatch))
  #           for strace in trace:
		# output.write("{};".format(strace))
	 #    output.write("\n")
            
    f.close()
    output=open(str(proj)+".regex.trace",'w')
    sum1="total # regexes: {}".format(len(dict_regex))
    output.write(sum1)
    output.write("\n")
    
    dict_pair=dict()
    for regex in dict_regex:
        dict_input_trace=dict_regex[regex]
        sum2="regex: {} total # inputs: {}".format(regex,len(dict_input_trace))
        output.write(sum2)
        output.write("\n")
       
	if regex not in dict_pair:
		dict_pair[regex]=set()
 
        for input_str in dict_input_trace:
            traces=dict_input_trace[input_str]
            sum3="regex: {} input: {} # traces: {}".format(regex,input_str,len(traces))
            output.write(sum3)
            output.write("\n")
            
            dict_trace=dict()
            for trace in traces:
                if trace not in dict_trace:
                    dict_trace[trace]=1
                else:
                    dict_trace[trace]+=1
            for trace,occur in dict_trace.items():
		output.write(str(occur))
		output.write(":")
		output.write(str(trace))
		output.write("\n")
	    output.write("\n")

	    dict_pair[regex].add(input_str)
       	        
    output.close() 

    print("finish picking regex")
    if len(dict_pair)>0:
        print("dump regex: ")
        print(str(proj)+".regex")
        output=open(str(proj)+".regex",'w')
        pickle.dump(dict_pair, output)
        output.close() 
        print("dump regex") 
        


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

