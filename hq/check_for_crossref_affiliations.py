# before running, activate dis env and put utility/bin in path like so:
# export PYTHONPATH="${PYTHONPATH}:/Users/scarlettv/dis-utilities/utility/bin"

import name_match as nm 


dois_to_check = []
with open('from_rob/not_in_mongo.txt', 'r') as instream:
    for doi in instream.read().splitlines():
        dois_to_check.append(doi.split()[0].strip())


dois_not_in_crossref = []
dois_w_no_author = []
dois_w_no_affil = []
dois_w_affil = []
for doi in dois_to_check:
    res = nm.JRC.call_crossref(doi)
    if 'message' in res:
        affils = []
        if 'author' in res['message']:
            for a in res['message']['author']:
                affils.append(a['affiliation'])
            affils = list(nm.flatten(affils))
        else:
            dois_w_no_author.append(doi)
            continue
        if affils:
            dois_w_affil.append(doi)
        else:
            dois_w_no_affil.append(doi)
    else:
        dois_not_in_crossref.append(doi)

with open('dois_w_no_author.txt', 'w') as outF:
    for doi in set(dois_w_no_author):
        outF.write(f"{doi}\n")

with open('dois_w_no_affiliations.txt', 'w') as outF:
    for doi in set(dois_w_no_affil):
        outF.write(f"{doi}\n")

with open('dois_w_affiliations.txt', 'w') as outF:
    for doi in set(dois_w_affil):
        outF.write(f"{doi}\n")

with open('dois_not_in_crossref.txt', 'w') as outF:
    for doi in set(dois_not_in_crossref):
        outF.write(f"{doi}\n")