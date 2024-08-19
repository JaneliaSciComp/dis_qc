import csv 
import requests
import json
import sys
import re

page = 1
length_of_last_page = 1
data = []
while length_of_last_page != 0:
	url = f"https://api.figshare.com/v2/articles?page_size=500&page={page}&institution=295" #&group=11380 or &group=49461
	print(f"Getting page {page}...")
	response = requests.get(url)
	if response.status_code != 200:
		sys.exit(1)
	length_of_last_page = len(response.json())
	page += 1
	for item_dic in response.json():
		data.append(item_dic)

not_v1 = [item_dic for item_dic in data if not item_dic['doi'].endswith(".v1")] 
#76 items from the API don't end with v1.

api_dois = [re.sub(r'\.v\d+$', '', item_dic['doi']) for item_dic in data]
#DOIs from the batch management don't have version numbers, for some reason, so I am stripping the version #s from the api dois.

#According to the API, we have 1422 public articles, all of which have a DOI. I checked, these aren't just empty fields.



file = open('/Users/scarlettv/Downloads/batch_download.csv', 'r')
lines = list(csv.reader(file, delimiter=',', quotechar='"'))
file.close()
header = lines[0]
lines = lines[1:] #remove header
batch_data = [ dict(zip(header, lines[n])) for n in range(len(lines)) ] 


# According to the batch tool, we have 1829 public articles, and 1765 of the public articles have a DOI. 
# According to the batch tool, we have 1897 total articles, and 1827 of the total articles have a DOI. 

batch_dois = []
for item in batch_data:
	if item['doi']:
		batch_dois.append(item['doi'])

missing_from_api = [doi for doi in batch_dois if doi not in api_dois]

with open('missing_from_api.tsv', 'w') as outF:
	for doi in missing_from_api:
		for item in batch_data:
			if item['doi'] == doi:
				to_print = dict(item) # make a copy
				del to_print['description'] #remove the 'description', which contains HTML code and looks very ugly when printed in a tsv
				tsv_str = "\t".join(list(to_print.values()))+"\n"
				outF.write(tsv_str)

