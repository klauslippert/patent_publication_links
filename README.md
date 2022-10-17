## Knowledge transfer from science to economy <br/> illustrated via patent - publication pairs: <br/> reducing ambiguities with word embeddings and references

This is the code repository to reproduce the results and figures from [my paper](LINK MISSING).

1. [Description](#description)
2. [Data Sources](#data-sources)
3. [Synopsis](#synopsis)
4. [Remarks](#remarks)
5. [File Description](#file-Description)
6. [Data Flow](#data-flow)


## Description

This repo builds up a [docker](https://www.docker.com/) container with all needed libaries and a Postgresql database for storing the intermediate stages and the results.

You can access the postgresql when the container is running, for the database credentials please see the output of the building script. The raw data files can be accessed anytime form outside the container.

```
└── home
    └── user        
        ├── code
        ├── data
        │   ├── patent                 persistent on local drive: stores raw patent data
        │   ├── postgresql             persistent on local drive: stores the DB
        │   └── publication            persistent on local drive: stores raw publication data
        └── figures
```

## Data Sources
- **Publication data** from the National Library of Medicine using the FTP server of NCBI
  - [homepage](https://pubmed.ncbi.nlm.nih.gov/)
  - [datasource](https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/)
- **Patent data** from the European Patent Office (EPO) using their htmls service
  - [homepage](https://www.epo.org)
  - [datasource](https://data.epo.org/publication-server/rest/v1.2/publication-dates)
- **MeSH** terms
  - german and english
  - french

## Synopsis
to be used inside a UNIX BASH
- install docker
- clone this repo
- run ```./quamedfo_publication/build_image.sh``` -> you end up in a BASH inside the container
- download the raw data manually. The EPO
- run ```/home/user/code

## remarks (Yes, i know, but ...)
- **YES**, you need a heavy machine to run those scripts in a reasonable amount of time. This work was part of the [QuaMedFo](https://www.wihoforschung.de/wihoforschung/de/bmbf-projektfoerderung/foerderlinien/quantitative-wissenschaftsforschung/quamedfo/quamedfo.html) Project where [ZB MED](https://www.zbmed.de/en) provides me with a heavy 40 CPU, 300 GB RAM VM. Reasonable time on this machine was still approx. 6 weeks.
- **YES**, you're root inside the docker container and you've persistant drives. The requirement of this repo is not to deliver a production ready secure container.
- **YES**, you need to be in the root group on your local machine. I could not solve the owner-ship issues of the persistant data folders and so you have to ```chown``` the folders to yourself each time you run the script again. If someone can solve those issues, please do a pull request, i would be very happy.
- **YES**, the download of the raw data is manual and will stay manual. Be happy, that the script realizes that the EPO download limit is reached and will stop and not fill quietly your xml with useless data. Wait a day or two and start it again.
- **YES**, the script uses the actual PubMed baseline data provided on the ftp-server. When you run it next year, you use different data for the publications. But in the observed time period 2000-2005 there should not be a lot of changes anymore (just guessing, I didn't check)
- **YES**, this scripts only use a static snapshoot of the data. If you want to extend this repo: there are no continious delta-load functions. Additionally, you need intermediate steps, that you e.g. don't do the long lasting processing again and again, but also handle growing patent families. This functionality will be soon implemented in the [ZB MED](https://www.zbmed.de/en) Search Portal for Live Sciences [LIVIVO](https://www.livivo.de/app?LANGUAGE=en), where you'll get the patent-publication links as additional information to the latest publication data (and not only PubMed), using the latest patent data.


## File Description
|script in /home/user/code|purpose|where to find the data|
|---|---|---|
|00_data_download_pubmed.py   |download PubMed Baseline xml-data and upload to Postgresql   | /home/user/data/publication|
|MISSING: DB upload PubmedBaseline    |TODO: split download and DB upload into two scripts!   |   |
| 000_data_download_epo.py  |download patent data from EPO   |  /home/user/data/patent|
|MISSING: DB upload EPO   |   |   |
| 00_simulate_uploaded_data_patents.sql   |||
| 00a_upload_MeSH_mainheadings.py |||
| 00b_functions.sql |||
| 04a_create_raw_pubmed_basline.sql       |||
| 04b_create_journalnorm_table.sql |||
| 04d_pubmed_names.sql |||                    
| 04_d2_enrich_pubmed_names_w_country.py  |||
| 04d_2_pubmed_names.sql |||       
| 04d_3_pubmed_names.sql |||     
| 04d_4_country_extract.py |||        
| 04d_4_country_extract_V2.py |||      
| 04d_4_country_extract_V3.py |||
| 04d_ext_pubmed_names.sql |||
| 04d_fin_pubmed_names.sql |||       
| 04e_pubmed_master.sql                   |||
| 05a_patente_names.sql        |||           
| 05b_process_patent_names.py    |||           
| 05c_patent_master.sql |||
| 06a_join_patent_publication.py |||
| 06a_join_patent_publication_incl_year.py |||
| 06b_dist_publications.sql |||
| 06c_dist_patents.sql  |||
| 07a_pubmed_mesh.sql |||      
| 08a_patente_mesh.sql |||
| 08b_MeSH_extract_ABKUERZUNG.sql |||
| 08b_MeSH_extract_KAPUTT.py |||          
| 08c_patente_mainheadings.sql |||              
| 09_bert_embed_ABKUERZUNG.sql |||           
| 09_bert_embed.py |||           
| 10_join_cosine_similarity.sql |||
| 11a_references_publication.sql |||
| 11a_references_publication_V2.sql          |||
| 11b_references_patents.sql|||
| 11c_enrich_patents_w_crossref.py|||
| 11d_common_references.sql |||
| 12_join_all.sql |||
| 13_pat_ipc.sql |||
| 14_join_all_ranked.sql |||





|script|what it does|comment|
|---|---|---|
| requirements.txt | for automatically installing all need Python libraries||
| my_pubmed_parser | pubmed parser from XXX with one small change by me||
| run.sh| main script to run the complete pipeline, except the download of raw data||
| country_name_iso_dict.p | data for normalizing country names to ISO codes||
| keyword_extraction.py | extracts keywords from text. here: extracts MeSH-Terms||
| med_mesh.sql | TODO: check if needed||
| LEGACY_04d_3_pubmed_names.sql |||
| LEGACY_05a_patente_names.sql ||| 
| LEGACY_05c_patent_master.sql |||
| LEGACY_pat_univ_applicants.sql |||
| db_credentials.sh |||
| PAT_get_data.py |||



---- 


{{< mermaid >}} 
    graph TB
    A --> B
{{< /mermaid >}}



## Data Flow
