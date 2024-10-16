import qcmodule as qc

minimum_date = qc.datetime(2024, 6, 1)
url = f'https://dis.int.janelia.org/doi/inserted/{str(minimum_date.date())}'
response = qc.get_request(url)
items = [ qc.create_item_object(doi_record) for doi_record in response['data'] ]
print(len(items))
