import csv
import re
import qcmodule as qc
from datetime import datetime

class OAW_Item:
	def __init__(self, doi=None, publisher=None, pub_date=None, institutions=None, rors=None, has_preprint_copy=None, preprint_doi=None):
		self.doi = doi
		self.publisher = publisher
		self.pub_date = datetime.strptime(pub_date, '%Y-%m-%d') if pub_date else None
		self.institutions = institutions
		self.rors = [strip_url_prefix(e) for e in rors.split(';')]
		self.has_preprint_copy = has_preprint_copy
		self.preprint_doi = preprint_doi
		self.in_o = None
		self.in_d = None
	
	def in_oaw(self):

	def 

# monkey patching
def in_oaw(self):





def strip_url_prefix(url):
    # Use a regular expression to match and remove everything up to and including '.org/'
    result = re.sub(r'^https?://[^/]+\.org/', '', url)
    return result


file = open('report_works_since_01Jan2007.csv', 'r')
lines = list(csv.reader(file, delimiter=',', quotechar='"'))
file.close()
oaw_items=[]
for n in range(1, len(lines)):
	line = lines[n]
	oaw_items.append(
		OAW_Item(doi=line[0], publisher=line[7], pub_date=line[1], institutions=line[15], rors=line[16], has_preprint_copy=line[28], preprint_doi=line[29])
	)

oaw_items = [i for i in oaw_items if '013sk6x84' in i.rors] 

# They are determining institution based on RORs, not ORCIDs:
# oaw_items1 = [i for i in oaw_items if '013sk6x84' in i.rors] #2406
# oaw_items2 = [i for i in oaw_items if 'Janelia' in i.institutions] #2406

#minimum_date = qc.datetime(2007, 1, 1)
minimum_date = qc.datetime(2024, 1, 1)
url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = qc.get_request(url)

print(f"Obtained {len(response['data'])} DOIs inserted after {minimum_date.date()}")
dis_items = [ qc.create_item_object(doi_record) for doi_record in response['data'] ]
dis_items = [ item for item in dis_items if item.item_type == 'preprint' or item.item_type == 'journal-article' ]
dis_dict = {item.doi: item for item in dis_items}

dis_DOIs = [item.doi for item in dis_items]
oaw_DOIs = [item.doi for item in oaw_items]
in_dis_but_not_oaw = set(dis_DOIs).difference(oaw_DOIs)
in_oaw_but_not_dis = set(oaw_DOIs).difference(dis_DOIs)
in_both = set(oaw_DOIs).intersection(dis_DOIs)

# >>> len(dis_items)
# 3013
# >>> len(in_dis_but_not_oaw)
# 1002
# >>> len(in_oaw_but_not_dis)
# 395
# >>> len(in_both)
# 2011

dis_only_dict = {dis_dict[s].doi: dis_dict[s] for s in in_dis_but_not_oaw }
dis_has_affiliations = [ any([a.affiliations for a in item.author_list]) for item in dis_only_dict.values() ]
dis_has_affiliations.count(True)
# 132
dis_has_affiliations.count(False)
# 870
# 85% of the papers that are in DIS DB, but not OAW, lack any author affiliations. 

dis_has_affiliations_dict = {dis_dict[s].doi: dis_dict[s] for s in in_dis_but_not_oaw if any([a.affiliations for a in dis_dict[s].author_list]) }
janelia = []
no_janelia = []
for item in dis_has_affiliations_dict.values():
	if 'Janelia' in ' '.join(item.get_affiliations()):
		janelia.append(item)
	else:
		no_janelia.append(item)

# Of those 870 papers, how many have a Janelian author, based on orcids?
jrc_author = 0
no_jrc_author = 0
for i in dis_has_affiliations_dict.values(): 
	if i.author_ids:
		jrc_author += 1
	else:
		no_jrc_author += 1

# Of those 132 papers that aren't in OAW and do have author affiliations, 31 of them don't mention janelia in the affiliations.
# >>> len(janelia)
# 101
# >>> len(no_janelia)
# 31

after2024 = 0
before2024 = 0
for item in janelia:
	if item.pub_date < qc.datetime(2024, 1, 1):
		before2024 += 1
	else:
		after2024 += 1

# >>> after2024
# 45
# >>> before2024
# 56
# Of those 101 papers that do have Janelia in the affiliations and which OAW missed, 45% are from 2024.

manual = []
sync = []
for item in dis_has_affiliations_dict.values():
	if item.load_source == 'Manual':
		manual.append(item)
	else:
		sync.append(item)

# Of those 132 papers that aren't in OAW and do have author affiliations, 130 of them were identified by sync (or by Jaime). 2 were identified by me.

all_manual = [ item for item in dis_items if item.load_source=='Manual' ]
oaw_items_dict = {item.doi: item for item in oaw_items}
manual_oaw_overlap = 0
for item in manual:
	if item.doi in oaw_items_dict:
		manual_oaw_overlap += 1

# None of the 23 items that I've found manually are in OA.Works.



