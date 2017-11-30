# -*- coding: utf-8 -*-
from multiprocessing import Pool
import urllib2
import sys
sys.path.append('/home/peipei/Enthought/Canopy_64bit/User/lib/python2.7/site-packages')

#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup

import ssl
#file = open("JavaProjectsWithUnitTest5.txt","w") 
file = open("JavaProjectsWithUnitTest_multiProcess.txt","w") 

#str1="http://reporeapers.github.io/results/"
str1="https://reporeapers.github.io/results/"
str2=".html"
context = ssl._create_unverified_context()
#for i in range(1,4496): ##4496 pages may have different headers different

def getPairs(headers):
    lst=[header.text.strip() for header in headers]   ##for links, headers[1].string is NoneType
    pairs={v:k for k,v in enumerate(lst)}
    return pairs
    
def processOnePage(i):
	page = urllib2.urlopen(''.join([str1,str(i),str2]),context=context)	 
	soup = BeautifulSoup(page.read(),"lxml")
	x = soup.body.find_all('tr') ## get all rows except table header
	pairs=getPairs(x[0].find_all('th'))
	print "headers: ", pairs
	#return
	r=-1 ##do not consider header		
	for rep in x:
			r+=1 #the row of the items on ith page
			elements=rep.find_all('td') ##get the columns of each row
			if len(elements)>10:  ##usually 0-14 == 15 columns
				print "r: ", r
				lan=elements[pairs.get(u'Language')].string
				unit=elements[pairs.get(u'Unit Test')].string
				#unit=float(elements[11].string)
				if lan=="Java" and unit!="None" and float(unit)>0.0:
				    hrefs=elements[pairs.get(u'Links')].find_all('a',href=True)
				    string_api=hrefs[0]['href']
				  #  print string_api
				    string_url=hrefs[1]['href']
				   # print string_url
				   # print elements[0].string, unit

				    v_api=True
				    try:
					urllib2.urlopen(string_api,context=context)
				    except urllib2.HTTPError, e:
					v_api=False
					print "api url http error: ", e.code
				    except urllib2.URLError, e:
					v_api=False
					print "api url url error: ", e.args

				    v_url=True
				    try:
					urllib2.urlopen(string_url,context=context)
				    except urllib2.HTTPError, e:
					v_url=False
					print "proj url http error: ", e.code
				    except urllib2.URLError, e:
					v_url=False
					print "proj url url error: ", e.args

				    file.write(str(i)) ## page in reporeaper
				    file.write("\t")
				    file.write(str(r-1)) ## row on the page of reporeaper
				    file.write("\t")

				    file.write(elements[pairs.get(u'Repository')].string) ##project name
				    file.write("\t")

				    file.write(str(unit)) ##unit
				    file.write("\t")

				    file.write(elements[pairs.get(u'Architecture')].string) ## architecture
				    file.write("\t")

				    file.write(elements[pairs.get(u'Community')].string) ## community/collaborator
				    file.write("\t")

				    file.write(elements[pairs.get(u'CI')].string) ## continuous integration
				    file.write("\t")

				    file.write(elements[pairs.get(u'Documentation')].string) ## documentation
				    file.write("\t")

				    file.write(elements[pairs.get(u'History')].string) ## history/evolution
				    file.write("\t")

                                    if u'Issues' in pairs:
				        file.write(elements[pairs.get(u'Issues')].string) ## issues
				    else:
				        file.write("NA") ## issues
				    file.write("\t")

				    file.write(elements[pairs.get(u'License')].string) ## license
				    file.write("\t")

                                    if u'Size' in pairs:
				        file.write(elements[pairs.get(u'Size')].string) ## size/code lines
				    else:
				        file.write("NA") ## size/code lines
				    file.write("\t")

				    file.write(elements[pairs.get(u'State')].string) ## state
				    file.write("\t")

				    file.write(elements[pairs.get(u'# Stars')].string) ## stars
				    file.write("\t")

				    file.write(elements[pairs.get(u'Timestamp')].string) ## timestamp
				    file.write("\t")

				    file.write(string_api) ##api
				    file.write("\t")
				    #file.write(v_api) ##api validation
				    file.write("1") if v_api else file.write("0")
				    file.write("\t")

				    file.write(string_url) #url
				    file.write("\t")
				    #file.write(v_url) #url validation
				    file.write("1") if v_url else file.write("0")
				    file.write("\n")
				    

if __name__ == '__main__':  ##python 2.7 version
	if sys.argv is None or len(sys.argv)<2: #
		sys.exit('Error! You need to specify begin and end or specific page number!!')
	if len(sys.argv)==2:
		page=sys.argv[1]	
		processOnePage(int(page)) ##1, 2914, 3707, 4400
		print "-----------end-----------"
		#processOnePage(4400)
	elif len(sys.argv)==3:
		begin=sys.argv[1]
		end=sys.argv[2]
		#pool = Pool(processes=2)            # start 4 worker processes ##intotal it has 4 cores
		#print(pool.map(processOnePage, range(int(begin),int(end))))       # prints "[0, 1, 4,..., 81]"
		#pool.terminate()
		for i in range(int(begin),int(end)):
			processOnePage(i)
