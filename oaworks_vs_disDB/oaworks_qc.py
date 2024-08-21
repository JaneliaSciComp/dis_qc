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
		self.in_d = None
	def in_dis(self, bool):
		self.in_d = bool



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

minimum_date = qc.datetime(2007, 1, 1)
url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = qc.get_request(url)

print(f"Obtained {len(response['data'])} DOIs inserted after {minimum_date.date()}")
dis_items = [ qc.create_item_object(doi_record) for doi_record in response['data'] ]
dis_items = [ item for item in dis_items if item.item_type == 'preprint' or item.item_type == 'journal-article' ]
oaw_dois = [item.doi for item in oaw_items]
for item in dis_items:
	if item.doi in oaw_dois:
		setattr(item, 'in_o', True)
	else:
		setattr(item, 'in_o', False)

dis_dict = {item.doi: item for item in dis_items}

for i, item in enumerate(oaw_items):
	if item.doi in dis_dict:
		oaw_items[i].in_dis(True)
	else:
		oaw_items[i].in_dis(False)


in_dis_but_not_oaw = [item for item in dis_items if item.in_o is False]
in_oaw_but_not_dis = [item for item in oaw_items if item.in_d is False]
in_both = set(dis_dict.keys()).intersection(oaw_dois)

# >>> len(dis_items)
# 3013
# >>> len(in_dis_but_not_oaw)
# 1002
# >>> len(in_oaw_but_not_dis)
# 395
# >>> len(in_both)
# 2011

#dis_only_dict = {dis_dict[s].doi: dis_dict[s] for s in in_dis_but_not_oaw }
dis_only_has_affiliations = [item for item in in_dis_but_not_oaw if item.has_affiliations()]
dis_only_lacks_affiliations = [item for item in in_dis_but_not_oaw if not item.has_affiliations()]

# len(dis_only_has_affiliations)
# 132
# 85% of the papers that are in DIS DB, but not OAW, lack any author affiliations. (870/1002)

janelia = []
no_janelia = []
for item in dis_only_has_affiliations:
	if 'Janelia' in ' '.join(item.affiliations):
		janelia.append(item)
	else:
		no_janelia.append(item)

# Of those 132 papers that aren't in OAW and do have author affiliations, 31 of them don't mention janelia in the affiliations.
# >>> len(janelia)
# 101
# >>> len(no_janelia)
# 31
# Spot checking these 31, they were probably added by Jaime. Several of them are former Janelians who used their janelia.org email, but didn't include janelia in their author affiliations.
# Some are janelians who only put HHMI in their affiliation.
# In at least one case, Janelia is mentioned on the affiliations in the website but is mysteriously absent from the crossref metadata.
# Basically, these are fringe/debatable cases.


# Of those 870 papers that lack affiliations, how many have a Janelian author, based on orcids?
jrc_author = []
no_jrc_author = []
for i in dis_only_lacks_affiliations: 
	if i.author_ids:
		jrc_author.append(i)
	else:
		no_jrc_author.append(i)

# >>> len(jrc_author)
# 600
# >>> len(no_jrc_author)
# 270
# About two thirds of them do have an author with a Janelia ORCID. (Or simply an employee Id manually added by me)

# So there's still a mysterious 270 papers that don't have any Janelia orcids and don't have any author affiliations. 
# Spot checking, most of them seem legit. There are some weird ones, e.g. broken DOIs, or alumni only, or no janelians/mention of janelia.

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
for item in dis_only_has_affiliations:
	if item.load_source == 'Manual':
		manual.append(item)
	else:
		sync.append(item)

# >>> len(manual)
# 2
# >>> len(sync)
# 130
# Of those 132 papers that aren't in OAW and do have author affiliations, 130 of them were identified by sync (or by Jaime). 2 were identified by me.

all_manual = [ item for item in dis_items if item.load_source=='Manual' ]
oaw_items_dict = {item.doi: item for item in oaw_items}
manual_oaw_overlap = 0
for item in manual:
	if item.doi in oaw_items_dict:
		manual_oaw_overlap += 1

# None of the 23 items that I've found manually are in OA.Works.

for item in no_jrc_author[0:16]: # the mysterious 270
	print(item.doi)

oaw_pp = [ item for item in oaw_items if item.has_preprint_copy=='true' ]
dis_pp = [ item for item in dis_items if item.item_type=='journal-article' and item.preprint_relation is True ]

