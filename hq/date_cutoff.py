# before running, activate dis env and put utility/bin in path like so:
# export PYTHONPATH="${PYTHONPATH}:/Users/scarlettv/dis-utilities/utility/bin"

import name_match as nm

dois = {}
with open('dois_w_no_affiliations.txt', 'r') as inF:
    for doi in inF.read().splitlines():
        dois[doi.split()[0].strip()] = {}

for doi in dois:
    res = nm.JRC.call_crossref(doi)
    if 'message' in res:
        dois[doi] = res['message']

dois_before_and_inc_2007 = []
dois_after_2007 = []
other = []
for doi, data in dois.items():
    if 'published' in data:
        if int(data['published']['date-parts'][0][0]) <= 2007:
            dois_before_and_inc_2007.append(doi)
        elif int(data['published']['date-parts'][0][0]) > 2007:
            dois_after_2007.append(doi)
    else:
        other.append(doi)

with open('dois_w_no_affiliations_after_2007.txt', 'w') as outF:
    for doi in dois_after_2007:
        outF.write(f"{doi}\n")