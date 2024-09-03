import csv
import re
import qcmodule as qc
from datetime import datetime
from collections import Counter

class OAW_Item:
	def __init__(self, doi=None, publisher=None, journal=None, pub_date=None, institutions=None, rors=None, has_preprint_copy=None, preprint_doi=None):
		self.doi = doi
		self.publisher = publisher
		self.journal = journal
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
		OAW_Item(doi=line[0], publisher=line[7], journal=line[8], pub_date=line[1], institutions=line[15], rors=line[16], has_preprint_copy=line[28], preprint_doi=line[29])
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
dis_items = [ item for item in dis_items if item.item_type == 'journal-article' ]
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

# with('in_dis_but_not_oaw.txt', 'w') as outF:
# 	for item in in_dis_but_not_oaw:
# 		print(f'{item.doi}\n')

# >>> len(dis_items)
# 2278
# >>> len(oaw_items)
# 2406
# >>> len(in_dis_but_not_oaw)
# 264
# >>> len(in_oaw_but_not_dis)
# 392
# >>> len(in_both)
# 2014

# Are we systematically missing certain journals?
journals = [item.journal for item in in_oaw_but_not_dis]
journal_counts = Counter(journals)
journal_counts_sorted = {k: v for k, v in sorted(journal_counts.items(), key=lambda item: item[1], reverse=True)}
with open('papers_we_missed_by_journal.csv', 'w') as outF: 
	for k, v in journal_counts_sorted.items():
		outF.write(f'{k},{v}\n')

# How many of these papers have any author affiliations?
dis_only_has_affiliations = [item for item in in_dis_but_not_oaw if item.has_affiliations()]
dis_only_lacks_affiliations = [item for item in in_dis_but_not_oaw if not item.has_affiliations()]

# len(dis_only_lacks_affiliations)
# 197
# 75% of the papers that are in DIS DB, but not OAW, lack any author affiliations. (197/264)

oaw_only_has_affiliations = [item for item in in_oaw_but_not_dis if item.rors]
oaw_only_lacks_affiliations = [item for item in in_oaw_but_not_dis if not item.rors]

# >>> len(oaw_only_has_affiliations)
# 392
# >>> len(oaw_only_lacks_affiliations)
# 0
# All OAW papers have affiliations.

# I added three papers (10.1016/j.bpj.2023.11.1743, 10.3389/fnins.2023.1337612, 10.1016/j.bbagen.2023.130449) to DIS DB that were in OAW but not DIS DB. 
# They had no author affiliations, so no mention of Janelia in the crossref metadata.
# This may be the case for all of the papers that we missed.

janelia = []
no_janelia = []
for item in dis_only_has_affiliations:
	if 'Janelia' in ' '.join(item.affiliations):
		janelia.append(item)
	else:
		no_janelia.append(item)

# Of those 67 papers that aren't in OAW and do have author affiliations, 29 of them don't mention janelia in the affiliations.
# >>> len(janelia)
# 38
# >>> len(no_janelia)
# 29
# Spot checking these 29, they were probably added by Jaime. Several of them are former Janelians who used their janelia.org email, but didn't include janelia in their author affiliations.
# Some are janelians who only put HHMI in their affiliation.
# In at least one case, Janelia is mentioned on the affiliations in the website but is mysteriously absent from the crossref metadata.
# Basically, these are fringe/debatable cases.


# Of those DIS-only papers that lack affiliations, how many have a Janelian author, based on orcids?
jrc_author = []
no_jrc_author = []
for i in dis_only_lacks_affiliations: 
	if i.author_ids:
		jrc_author.append(i)
	else:
		no_jrc_author.append(i)

# >>> len(jrc_author)
# 92
# >>> len(no_jrc_author)
# 105
# About half of them do have an author with a Janelia ORCID. (Or simply an employee Id manually added)

# So there's still a mysterious 105 papers that don't have any Janelia orcids and don't have any author affiliations. 
# Spot checking, most of them seem legit. There are some weird ones, e.g. broken DOIs, or alumni only, or no janelians/mention of janelia.

after2024 = 0
before2024 = 0
for item in janelia:
	if item.pub_date < qc.datetime(2024, 1, 1):
		before2024 += 1
	else:
		after2024 += 1

# >>> after2024
# 18
# >>> before2024
# 20
# Of those 38 papers that do have Janelia in the affiliations and which OAW missed, about half are from 2024.
thisyear_oaw = [item for item in oaw_items if item.pub_date > qc.datetime(2024, 1, 1)]
thisyear_dis = [item for item in dis_items if item.pub_date > qc.datetime(2024, 1, 1)]
# >>> len(thisyear_oaw)
# 63
# >>> len(thisyear_dis)
# 111


manual = []
sync = []
for item in dis_only_has_affiliations:
	if item.load_source == 'Manual':
		manual.append(item)
	else:
		sync.append(item)

# >>> len(manual)
# 1
# >>> len(sync)
# 66
# Of those 67 papers that aren't in OAW and do have author affiliations, Only one was identified by me.

all_manual = [ item for item in dis_items if item.load_source=='Manual' ]
oaw_items_dict = {item.doi: item for item in oaw_items}
manual_oaw_overlap = 0
for item in manual:
	if item.doi in oaw_items_dict:
		manual_oaw_overlap += 1

# None of the 9 papers that I've found manually are in OA.Works.

oaw_pp = [ item for item in oaw_items if item.has_preprint_copy=='true' ]
dis_pp = [ item for item in dis_items if item.item_type=='journal-article' and item.preprint_relation != () and item.preprint_relation[0] == 'has-preprint' ]

# >>> len(oaw_pp)
# 435
# >>> len(dis_pp)
# 459

pp_ratio_by_year = {}
for y in range(2007, 2025):
	oaw_pp_y = len([item for item in oaw_pp if qc.datetime(y, 1, 1) < item.pub_date and item.pub_date < qc.datetime(y+1, 1, 1) ])
	oaw_nopp_y = len([ item for item in oaw_items if item.has_preprint_copy=='false' and qc.datetime(y, 1, 1) < item.pub_date and item.pub_date < qc.datetime(y+1, 1, 1)])
	dis_pp_y = len([item for item in dis_pp if qc.datetime(y, 1, 1) < item.pub_date and item.pub_date < qc.datetime(y+1, 1, 1) ])
	dis_nopp_y = len([ item for item in dis_items if item.item_type=='journal-article' and item.preprint_relation == () and qc.datetime(y, 1, 1) < item.pub_date and item.pub_date < qc.datetime(y+1, 1, 1)])
	pp_ratio_by_year[str(y)] = [
		oaw_pp_y/(oaw_pp_y+oaw_nopp_y), 
		dis_pp_y/(dis_pp_y+dis_nopp_y)
		]

with open('preprint_ratios.csv', 'w') as outF:
	outF.write('Year,OAW: papers with a preprint,DIS: papers with a preprint\n')
	for y, v in pp_ratio_by_year.items():
		outF.write(f'{y},{round(v[0]*100, 1)}%,{round(v[1]*100, 1)}%\n')

