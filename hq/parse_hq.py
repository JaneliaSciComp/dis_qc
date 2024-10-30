import json

d = {}
with open('from_rob/hq_with_tags.json', 'r') as inF:
    d = json.load(inF)

legit_dois = []
false_dois = []
with open('curated_manually/dois_w_no_affiliations_after_2007_curated.txt', 'r') as inF:
    lines = inF.readlines()
    for line in lines:
        if "- YES!" in line:
            legit_dois.append(line.split()[0])
            continue
        if "- No" in line:
            false_dois.append(line.split()[0])

legit_dois = set(legit_dois)
false_dois = set(false_dois)

legit_dois_w_tags = []
false_dois_w_tags = []
for item in d:
    if item['DOI']:
        if item['DOI'] in legit_dois:
            legit_dois_w_tags.append(item["DOI"])
            continue
        if item['DOI'] in false_dois:
            false_dois_w_tags.append(item["DOI"])

legit_dois_w_tags = set(legit_dois_w_tags)
false_dois_w_tags = set(false_dois_w_tags)
