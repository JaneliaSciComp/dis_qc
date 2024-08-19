import csv 
from ..paper_discovery_manual_vs_sync import newsletter_sources as ns

file = open('/Users/scarlettv/Downloads/report_works_since_01Jan2007.csv', 'r')
lines = list(csv.reader(file, delimiter=',', quotechar='"'))
file.close()
header = lines[0]
lines = lines[1:] #remove header
batch_data = [ dict(zip(header, lines[n])) for n in range(len(lines)) ] 


class OAW_Item:
	def __init__(self, doi=None, publisher=None, pub_date=None, rors=None, has_preprint_copy=None, preprint_doi=None):
		self.doi = doi
		self.publisher = publisher
		self.pub_date = datetime.strptime(pub_date, '%Y-%m-%d') if pub_date else None
		self.rors = self.rors
		self.has_preprint_copy = has_preprint_copy
		self.preprint_doi = preprint_doi

minimum_date = datetime(2007, 1, 1)

url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = get_request(url)
print(f"Obtained {len(response['data'])} DOIs inserted after {minimum_date.date()}")
items = [ create_item_object(doi_record) for doi_record in response['data'] ]
item_dict = {item.doi: item for item in items}

dois_from_spreadsheet = []
with open(insertions_file, 'r') as file:
    lines = file.readlines()
    dois_from_spreadsheet = [ line.split('\t')[0] for line in lines ]

items_from_spreadsheet = [ item_dict[doi] for doi in dois_from_spreadsheet ]
papers = [ item for item in items_from_spreadsheet if item.source == 'Crossref' or item.doi.startswith('10.48550/arXiv') ]
papers = [paper for paper in papers if is_no_more_than_four_weeks_older(paper.pub_date, minimum_date)]
