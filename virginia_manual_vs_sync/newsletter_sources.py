import qcmodule as qc
from datetime import timedelta

"""
This script parses a spreadsheet of recently inserted DOIs, downloaded from the DIS DB web interface.
Output: a new spreadsheet with more relevant metadata. 
The name of the file is hard-coded in this script.
I am using June 1st as my 'inserted since' date since that's about when the DIS pipeline started working pretty reliably.
"""


def is_within_six_days(date1, date2):
	delta = date2 - date1
	return timedelta(0) <= delta <= timedelta(days=6)

def is_no_more_than_four_weeks_older(date1, date2):
	four_weeks_prior = date2 - timedelta(weeks=4)
	return(date1 > four_weeks_prior)


#### CONSTANTS YOU SHOULD EDIT ###
insertions_file = 'jrc_inserted_since_Jun012024.tsv'
minimum_date = qc.datetime(2024, 6, 1)
##########

url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = qc.get_request(url)
print(f"Obtained {len(response['data'])} DOIs inserted after {minimum_date.date()}")
items = [ qc.create_item_object(doi_record) for doi_record in response['data'] ]
item_dict = {item.doi: item for item in items}

dois_from_spreadsheet = []
with open(insertions_file, 'r') as file:
	lines = file.readlines()
	dois_from_spreadsheet = [ line.split('\t')[0] for line in lines ]

items_from_spreadsheet = [ item_dict[doi] for doi in dois_from_spreadsheet ]
papers = [ item for item in items_from_spreadsheet if item.source == 'Crossref' or item.doi.startswith('10.48550/arXiv') ]
papers = [paper for paper in papers if is_no_more_than_four_weeks_older(paper.pub_date, minimum_date)]
batches = {} 
no_newsletter = []
for paper in papers:
	if paper.newsletter:
		if str(paper.newsletter.date()) in batches:
			batches[str(paper.newsletter.date())].append(paper)
		else:
			batches[str(paper.newsletter.date())] = [paper]
	else:
		no_newsletter.append(paper)

for paper in no_newsletter:
	for k, v in batches.items():
		if is_within_six_days(paper.insert_date, v[0].newsletter):
			batches[k].append(paper)
			continue

final_items = 0
with open( f"manual_vs_sync_{str(minimum_date.date())}_to_{qc.datetime.today().strftime('%Y-%m-%d')}.tsv", 'w' ) as outfile:
	outfile.write('DOI\tItem type\tLoad source\tPublisher\tPublication date\tInserted date\tNewsletter\tHas related items?\tHas affiliations?\n')
	for k, v in batches.items():
		for item in v:
			affiliations = any([a.affiliations for a in item.author_list])
			news_str = 'None'
			if item.newsletter:
				news_str = item.newsletter.date()
			outfile.write(f'{item.doi}\t{item.item_type}\t{item.load_source}\t{item.publisher}\t{item.pub_date.date()}\t{item.insert_date.date()}\t{news_str}\t{item.has_relations}\t{affiliations}\n')
			final_items += 1
		outfile.write('\n')




