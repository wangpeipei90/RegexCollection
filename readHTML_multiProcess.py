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
#for i in range(1,4496): ##4496 has headers different from previous 4495
def processOnePage(i):
	page = urllib2.urlopen(''.join([str1,str(i),str2]),context=context)	 
	soup = BeautifulSoup(page.read(),"lxml")
	x = soup.body.find_all('tr') ## get all rows except table header
	
	r=0		
	for rep in x:
			r+=1 #the row of the items on ith page
			elements=rep.find_all('td') ##get the columns of each row
			if len(elements)>10:  ##usually 0-14 == 15 columns
			    ##0: repository name
			    ##1: links
			    ##2: Languages
			    ##3: Architecture
			    ##4: Community
			    ##5: CI
			    ##6: Documentation
			    ##7: History
			    ##8: License
			    ##9: Management
			    ##10: Size
			    ##11: Unit Test could be None, 0.0, or float
			    ##12: State
			    ##13: Stars
			    ##14: Timestamp
				lan=elements[2].string
				unit=elements[11].string
				#unit=float(elements[11].string)
				if lan=="Java" and unit!="None" and float(unit)>0.0:
				    hrefs=elements[1].find_all('a',href=True)
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
					print(e.code)
				    except urllib2.URLError, e:
					v_api=False
					print(e.args)

				    v_url=True
				    try:
					urllib2.urlopen(string_url,context=context)
				    except urllib2.HTTPError, e:
					v_url=False
					print(e.code)
				    except urllib2.URLError, e:
					v_url=False
					print(e.args)

				    file.write(str(i)) ## page in reporeaper
				    file.write("\t")
				    file.write(str(r-1)) ## row on the page of reporeaper
				    file.write("\t")

				    file.write(elements[0].string) ##project name
				    file.write("\t")

				    file.write(str(unit)) ##unit
				    file.write("\t")

				    file.write(elements[3].string) ## architecture
				    file.write("\t")

				    file.write(elements[4].string) ## community/collaborator
				    file.write("\t")

				    file.write(elements[5].string) ## continuous integration
				    file.write("\t")

				    file.write(elements[6].string) ## documentation
				    file.write("\t")

				    file.write(elements[7].string) ## history/evolution
				    file.write("\t")

				    file.write(elements[8].string) ## issues
				    file.write("\t")

				    file.write(elements[9].string) ## license
				    file.write("\t")

				    file.write(elements[10].string) ## size/code lines
				    file.write("\t")

				    file.write(elements[12].string) ## state
				    file.write("\t")

				    file.write(elements[13].string) ## stars
				    file.write("\t")

				    file.write(elements[14].string) ## timestamp
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
        pool = Pool(processes=2)            # start 4 worker processes ##intotal it has 4 cores
        print(pool.map(processOnePage, range(2914,3000)))       # prints "[0, 1, 4,..., 81]"
        pool.terminate()