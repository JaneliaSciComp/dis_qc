import csv
import qcmodule as qc
from datetime import datetime

class OAW_Item:
	def __init__(self, doi=None, publisher=None, pub_date=None, rors=None, has_preprint_copy=None, preprint_doi=None):
		self.doi = doi
		self.publisher = publisher
		self.pub_date = datetime.strptime(pub_date, '%Y-%m-%d') if pub_date else None
		self.rors = rors
		self.has_preprint_copy = has_preprint_copy
		self.preprint_doi = preprint_doi

file = open('report_works_since_01Jan2007.csv', 'r')
lines = list(csv.reader(file, delimiter=',', quotechar='"'))
file.close()
oaw_items=[]
for n in range(1, len(lines)):
	line = lines[n]
	oaw_items.append(
		OAW_Item(doi=line[0], publisher=line[7], pub_date=line[1], rors=line[16], has_preprint_copy=line[28], preprint_doi=line[29])
	)


minimum_date = qc.datetime(2007, 1, 1)
url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = qc.get_request(url)
print(f"Obtained {len(response['data'])} DOIs inserted after {minimum_date.date()}")
dis_items = [ qc.create_item_object(doi_record) for doi_record in response['data'] ]


