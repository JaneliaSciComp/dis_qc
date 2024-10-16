# before running, activate dis env and put utility/bin in path like so:
# export PYTHONPATH="${PYTHONPATH}:/Users/scarlettv/dis-utilities/utility/bin"

import name_match as nm
import re

dois = {}
with open('dois_w_affiliations.txt', 'r') as inF:
    for doi in inF.read().splitlines():
        dois[doi.split()[0].strip()] = {}

for doi in dois:
    res = nm.JRC.call_crossref(doi)
    if 'message' in res:
        dois[doi] = res['message']

doi_affils = {}
janelia_dois = []
for doi, data in dois.items():
    affils = []
    if 'author' in data:
        for authdict in data['author']:
            for affil_dict in authdict['affiliation']:
                affils.append(affil_dict['name'])
    affils_concat_str = ' '.join(affils)
    doi_affils[doi] = affils_concat_str
    if re.search(r'Janelia', affils_concat_str):
        janelia_dois.append(doi)

# with open('temp.txt', 'w') as outF:
#     for doi, affils in doi_affils.items():
#         outF.write(f'{doi}\n{affils}\n')
