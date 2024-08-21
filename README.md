Here are some quick and dirty scripts to evaluate Janelia's new publication database, which was built by Rob Svirskas in May 2024 for the Data and Information Services department (DIS). Software for that pipeline is in the repository JaneliaSciComp/dis-utilities. 

In this repository, I'm comparing our database to two other data sources: 
1) Jaime Palay's data recorded in EndNote (which was imported into our database). These works were gathered entirely manually, and I'm not sure when she started gathering them. 
2) A spreadsheet downloaded from the dashboard that OA.Works made for HHMI. 

I also compared Janelia's figshare data downloaded from the API to those data downloaded using the figshare batch management tool, since we noticed that we get more DOIs from the website than from the API. (Conclusion: it turns out that the API doesn't return draft or private articles.) 
