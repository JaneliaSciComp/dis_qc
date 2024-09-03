Here are some quick and dirty scripts to evaluate Janelia's new publication database, which was built by Rob Svirskas in May 2024 for the Data and Information Services department (DIS). Software for that pipeline is in the repository [JaneliaSciComp/dis-utilities](https://github.com/JaneliaSciComp/dis-utilities). 

In oaworks_vs_disDB/, I'm comparing our database to a spreadsheet I downloaded from OA.Works' HHMI dashboard. 

In figshareAPI_vs_batch_management/, I compared Janelia's figshare data downloaded from the API to those data downloaded using the figshare batch management tool, since we noticed that we get more DOIs from the website than from the API. (Conclusion: it turns out that the API doesn't return draft or private articles.) 

In virginia_manual_vs_sync/, I looked at the papers I've found each week--the truly novel ones that we want to promote--and counted how many articles were found manually vs. how many were found through our automated system. The yellow rows on the spreadsheet indicate papers that the system really "should have found"--it turned out that none of these had Janelia in the author affiliations. I didn't highlight bioRxiv papers in the affiliations since we already knew that these often lack author affiliations in the Crossref metadata.
