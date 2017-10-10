import csv;
with open('dataset.csv','rb') as csvfile:
#	reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	reader = csv.reader(csvfile)
#	reader = csv.DictReader(csvfile, delimiter=' ', quotechar='|')
	for row in reader:
		#print(row);
#		print(row.length);
		if len(row)>9 and row[1]=="Java" and row[9]!="None" and float(row[9])>0.2: #language
			print(row[0],row[9]); #repository, unit_test		
