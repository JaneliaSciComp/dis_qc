We noticed that the figshare API says that Janelia has 1422 public articles, while their website says we have 1829 public articles. TLDR; My conclusion is that the API is just filtering out low-quality items, so I think we are fine.
 
It appears that their API makes some opinionated choices for us:
The API only returns items that have DOIs. (Janelia has 70 articles without a DOI.)
The API does not return articles that have a status of ‘private’ or ‘draft’. I don’t know what exactly that means (‘private’ is a figshare term, but ‘draft’ is a DOI state?!), but when I sampled a few of the DOIs in my browser, they were all broken links. There were 475 of these broken articles, so I believe these are the bulk of the discrepancy.
 
The figshare website also makes an opinionated choice:
It collapses DOIs that have the same version number. We have 76 DOIs with a version > .v1, so in fact the total number of Janelia figshare articles should be 1905.
 
I think the reason the numbers don’t add up perfectly is because of these differences in how each data source presents its DOIs. But 400-ish articles were missing from the API, 400-ish articles are broken (that is, the DOI links don't work) on the website, and 100% of the missing articles are broken (that is, they are private or draft), so… I consider this mystery solved.
