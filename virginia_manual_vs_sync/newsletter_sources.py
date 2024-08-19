import requests
from datetime import datetime, timedelta

"""
This script parses a spreadsheet of recently inserted DOIs, and produces a new spreadsheet with more relevant metadata. 
The input file must be downloaded from the DIS DB web interface, on the 'DOIs by insertion date' page.
The name of the file is hard-coded in this script, right under 'if __name__ == '__main__''.
I am using June 1st as my 'inserted since' date since that's about when the DIS pipeline started working pretty reliably.
"""

class Item:
	def __init__(self, doi=None, source=None, publisher=None, pub_date=None, load_source=None, insert_date=None, newsletter=None, has_relations=None, preprint_relation=None, item_type=None):
		self.doi = doi
		self.source = source
		self.publisher = publisher
		self.pub_date = datetime.strptime(pub_date, '%Y-%m-%d') if pub_date else None
		self.load_source = load_source
		self.insert_date = datetime.strptime(insert_date, '%a, %d %b %Y %H:%M:%S %Z') if insert_date else None 
		self.newsletter = datetime.strptime(newsletter.split()[0], '%Y-%m-%d') if newsletter else None
		self.has_relations = has_relations
		self.preprint_relation = preprint_relation if preprint_relation is not None else ()
		self.item_type = item_type
		self.author_list = []
	
	def add_authors(self, authors):
		self.author_list.extend(authors)


class Author:
	""" Author objects are constructed solely from the Crossref-provided author information. """
	def __init__(self, name, orcid=None, affiliations=None):
		self.name = name
		self.orcid = orcid
		self.affiliations = affiliations if affiliations is not None else [] # Need to avoid the python mutable arguments trap


#### Functions related to item objects ####

def create_item_object(doi_record):
	item = Item(
	doi = doi_record['doi'] if 'doi' in doi_record else doi_record['DOI'], # In DIS DB, DataCite only has DOI; Crossref has both doi and DOI
	source = doi_record['jrc_obtained_from'],
	publisher = doi_record['publisher'],
	pub_date = doi_record['jrc_publishing_date'],
	load_source = doi_record['jrc_load_source'],
	insert_date = doi_record['jrc_inserted'],
	newsletter = doi_record['jrc_newsletter'] if 'jrc_newsletter' in doi_record else None,
	has_relations = get_relation_boolean(doi_record),
	preprint_relation = get_preprint_relation(doi_record),
	item_type = get_type(doi_record)
	)
	if 'author' in doi_record:
		item.add_authors(create_author_objects(doi_record['author']))
	else:
		item.add_authors(create_author_objects(doi_record['creators']))
	return(item)

def get_relation_boolean(doi_record):
	if 'relation' in doi_record: #crossref
			return(True if doi_record['relation'] else False)
	else: # datacite
		return(True if 'relatedIdentifiers' in doi_record and doi_record['relatedIdentifiers'] else False)

def get_type(doi_record):
	if 'type' in doi_record: # crossref
		if doi_record['type'] == 'journal-article':
			return('Journal article')
		if doi_record['type'] == 'posted-content':
			if doi_record['subtype'] == 'preprint':
				return('Preprint')
	else: # datacite
		return(doi_record['types']['resourceTypeGeneral'])

def get_preprint_relation(doi_record):
	if 'jrc_preprint' in doi_record: # Note jrc_preprint is a list
		if 'type' in doi_record and doi_record['type'] == 'journal-article':
			return( ('has-preprint', doi_record['jrc_preprint']) )
		if 'type' in doi_record and doi_record['type'] == 'posted-content' and 'subtype' in doi_record and doi_record['subtype'] == 'preprint':
			return( ('is-preprint-of', doi_record['jrc_preprint']) )
		if 'arxiv' in doi_record['doi']:
			return( ('is-preprint-of', doi_record['jrc_preprint']) )
	else:
		return(None)

#### Function related to author objects ####

def create_author_objects(authors_list): # Ingests 'creators' (DataCite) or 'author' (Crossref)
	author_objects = []
	for author_record in authors_list:
		current_author = None
		if 'given' in author_record and 'family' in author_record: # Crossref
			full_name = ' '.join((author_record['given'], author_record['family']))
			current_author = Author( full_name )
		if 'givenName' in author_record and 'familyName' in author_record: # DataCite
			full_name = ' '.join((author_record['givenName'], author_record['familyName']))
			current_author = Author( full_name )
		if not current_author:
			if 'name' in author_record: # Sometimes 'name' is 'Scarlett, Virginia', so I'd rather concatenate first and last names 
				current_author = Author( author_record['name'] )
		if not current_author:
			for key in ['given', 'family', 'givenName', 'familyName']:
						if key in author_record:
							current_author = Author( author_record[key] )				
		if not current_author:
			print(author_record)
			raise AttributeError
		if 'affiliation' in author_record and author_record['affiliation']:
			for affiliation in author_record['affiliation']:
				if isinstance(affiliation, str): # DataCite
					current_author.affiliations.append(affiliation)
				elif 'name' in affiliation: # Crossref
					current_author.affiliations.append(affiliation['name'])
		if 'ORCID' in author_record: # Crossref
			current_author.orcid = strip_orcid_if_provided_as_url(author_record['ORCID'])
		if 'nameIdentifiers' in author_record and author_record['nameIdentifiers']: # DataCite
			for id_info_dic in author_record['nameIdentifiers']:
				if 'nameIdentifierScheme' in id_info_dic:
					if id_info_dic['nameIdentifierScheme'] == 'ORCID': 
						current_author.orcid = strip_orcid_if_provided_as_url(id_info_dic['nameIdentifier']) # I'm willing to bet that the first item in this list will be an ORCID
		author_objects.append(current_author)
	return(author_objects)


#### Misc low-level functions ####

def get_request(url):
	headers = { 'Content-Type': 'application/json' }
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return(response.json())
	else:
		print(f"There was an error with the API GET request. Status code: {response.status_code}.\n Error message: {response.reason}")
		sys.exit(1)

def replace_slashes_in_doi(doi):
	return( doi.replace("/", "%2F") ) # e.g. 10.1186/s12859-024-05732-7 becomes 10.1186%2Fs12859-024-05732-7

def strip_orcid_if_provided_as_url(orcid):
	prefixes = ["http://orcid.org/", "https://orcid.org/"]
	for prefix in prefixes:
		if orcid.startswith(prefix):
			return orcid[len(prefix):]
	return(orcid)

def is_within_six_days(date1, date2):
	delta = date2 - date1
	return timedelta(0) <= delta <= timedelta(days=6)

def is_no_more_than_four_weeks_older(date1, date2):
	six_weeks_prior = date2 - timedelta(weeks=4)
	return(date1 > six_weeks_prior)


# ---------------------------------------------------

if __name__ == '__main__':
	#### CONSTANTS YOU SHOULD EDIT ###
	insertions_file = 'jrc_inserted_since_Jun012024.tsv'
	minimum_date = datetime(2024, 6, 1)
	##########

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
	with open( f'manual_vs_sync_{str(minimum_date.date())}_to_{datetime.today().strftime('%Y-%m-%d')}.tsv', 'w' ) as outfile:
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




