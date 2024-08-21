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



## Data Flow
```mermaid
    graph TB
subgraph get data -> files
    EPO-->|funct02_01|file:/data/patent
    PubMed-->|funct01_01|file:/data/publication
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph files -> DB: stage
    file:/data/patent-->|funct02_02...funct02_05|patent.stage
    file:/data/publication-->|funct01_01|pubmed_baseline.stage
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph raw
    subgraph json/xml
        patent.stage-->|funct03_01|patent.raw
        pubmed_baseline.stage-->|funct03_01|pubmed_baseline.raw
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    subgraph relational
        pubmed_baseline.raw-->|funct03_02|publ.raw_pubmed_baseline
        patent.raw-->|funct03_03|publ.raw_patente
    end
end    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph 1. JOIN by names
    subgraph Process names pubmed
    publ.raw_pubmed_baseline-->|funct04_01|publ.names_pubmed_baseline
    publ.names_pubmed_baseline-->|funct04_02|publ.tmp_extract_country_iso
    publ.names_pubmed_baseline-->|funct04_03|publ.names_ext_pubmed_baseline
    publ.tmp_extract_country_iso-->|funct04_03|publ.names_ext_pubmed_baseline
    publ.names_ext_pubmed_baseline-->|funct04_04|publ.master_pubmed_baseline
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    subgraph Process names patente
    publ.raw_patente-->|funct05_01|publ.names_raw_patente
    publ.names_raw_patente--->|funct05_02|publ.names_patente
    publ.names_patente-->|funct05_03|publ.master_patente
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    publ.master_pubmed_baseline-->|funct06_01|publ.join_raw
    publ.master_patente-->|funct06_01|publ.join_raw
    publ.join_raw-->|funct06_02|publ.dist_publication
    publ.join_raw-->|funct06_03|publ.dist_patents
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph 2. content similarity
    publ.raw_pubmed_baseline-->|funct07_01|publ.mesh_pubmed_baseline
    publ.dist_publication-->publ.mesh_pubmed_baseline
    %%%%%%%%%%%%%%%%%%%%%%%
    publ.dist_patents-->publ.text_patente
    publ.raw_patente-->|funct08_01|publ.text_patente
    publ.text_patente-->|funct08_02|publ.text_patente_proc
    publ.text_patente_proc-->|funct08_03|publ.text_patente_proc
    publ.text_patente_proc-->|funct08_04|publ.mesh_patente
    %%%%%%%%%%%%%%%%%%%%%%%%
    publ.mesh_patente-->|funt09_01|publ.embed_bert_pubmed_baseline
    publ.mesh_pubmed_baseline-->|funt09_01|publ.embed_bert_patente
    %%%%%%%%%%%%%%%%%%%%%%%%%
    publ.embed_bert_pubmed_baseline-->|funct10_01|publ.join_cos_sim
    publ.embed_bert_patente-->|funct10_01|publ.join_cos_sim
    publ.join_raw-->publ.join_cos_sim
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
_[ ]-->|funct11_01|publ.journal_normalize
%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph 3. common references
    pubmed_baseline.stage-->|funct11_02|publ.ref_pubmed_baseline
    publ.dist_publication-->publ.ref_pubmed_baseline
    %%%%%%%%%%%%%%%%%%%%%%%%%%
    publ.raw_patente-->|funct11_03|publ.ref_raw_patents
    publ.dist_patents-->publ.ref_raw_patents
    publ.journal_normalize-->publ.ref_raw_patents
    publ.ref_raw_patents-->|funct11_04|publ.ref_raw_patents
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%
    publ.join_raw-->publ.join_common_refs
    publ.ref_pubmed_baseline-->|funct11_05|publ.join_common_refs
    publ.ref_raw_patents-->|funct11_05|publ.join_common_refs
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subgraph 4. ranking
    publ.raw_patente--->|funct12_01|publ.pat_ipc
    publ.join_raw--->|funct12_02|publ.join_all
    publ.join_common_refs--->|funct12_02|publ.join_all
    publ.join_cos_sim--->|funct12_02|publ.join_all
    publ.pat_ipc-->|funct12_02|publ.join_all

    publ.join_all-->|funct12_03|publ.join_all_ranked
end
```


## File Description
| |script in /home/user/code|purpose|
|---|---|---|
| | run.sh| main script to run the complete pipeline. Since there might be problems with the amount of data downloaded from EPO or PubMed, I recommend using the download scripts manually, comment them out in this file and run the rest automatically.|   
| --- | --- | --- | --- |
|preparation  |funct00_01_create_schemas_and_extensions.sql | creates needed schemas and extensions on the PostgresQL database  |  
||funct00_02_SQL_functions.sql | create db-function for finding emailendings in text |   
||funct00_03_upload_MeSH_mainheadings.py  | upload the MeSH terms   |  
||funct00_04_countrycodes_for_emailendings.py | ISO countrycodes used by country-detection via emailending  |  
||funct00_05_countrynames_for_keywordextraction.py | ISO countrynamens used for country-detection  |  
| --- | --- | --- | --- |
|get publication data|funct01_01_data_download_pubmed.py | downloads the publication data from PubMed. If you're a company. Pls check the legal rules for commercial / non-commercial use of this data yourself. better **run this manually**, because of  download limit from PubMed |   
| --- | --- | --- | --- |
|get patent data|funct02_01_data_download_epo.py | downloads the patent data from EPO as xml; **better run this manually**, because of download limit from EPO. When you're over the download limit, EPO will give you a valid xml with no useful data inside.  |  
||funct02_02_create_patent_filelist.py | creates a list of all patentfiles, needed for upload to postgres  |  
||funct02_03_create_table_patent_stage.sql | nomen est omen  |  
||funct02_04_patent_xml_upload.sh | nomen est omen  |  
||funct02_05_parse_pat_xml.py |  helper script for funct02_04, dealing with enconding |  
| --- | --- | --- | --- |
|create flat tables|funct03_01_create_pub_pat_raw.sql | creates postgres table for publication data  |  
||funct03_02_create_unnested_pubmed_baseline.sql | unnest the publication xml into flat tables  |  
||funct03_03_create_unnested_patente.sql |  unnest the patente xml into flat tables |  
| --- | --- | --- | --- |
| process publication data| funct04_01_proc_pubmed_names.sql |  process publication author names |  
||funct04_02_country_extract.py | extract countries from authors affiliation  |  
||funct04_03_normalize_pubmed_names.sql |  normalize publication author names |  
||funct04_04_pubmed_master.sql |   |  
| --- | --- | --- | --- |
|process patent data|funct05_01_patente_names.sql |   |  
||funct05_02_process_patent_names.py |   |  
||funct05_03_patent_master.sql |   |  
| --- | --- | --- | --- |
|create raw publication patent pairs|funct06_01_join_patent_publication.py |   |  
||funct06_02_dist_publications.sql |   |  
||funct06_03_dist_patents.sql |   |  
| --- | --- | --- | --- |
|extract MeSH from publications|funct07_01_pubmed_mesh.sql |   |  
| --- | --- | --- | --- |
|extract MeSH from patents|funct08_01_patente_mesh.sql |   |  
||funct08_02_table_text_patente_proc.sql |   |  
||funct08_03_MeSH_extract.py |   |  
||funct08_04_patente_mainheadings.sql |   |  
| --- | --- | --- | --- |
|create embeddings|funct09_01_bert_embed.py |   |  
| --- | --- | --- | --- |
|calc cosine similarity|funct10_01_join_cosine_similarity.sql |   |  
| --- | --- | --- | --- |
|common references|funct11_01_create_journalnorm_table.sql |   |  
||funct11_03_references_patents.sql |   |  
||funct11_02_references_publication.sql |   |  
||funct11_04_enrich_patents_w_crossref.py |   |  
||funct11_05_common_references.sql |   |  
| --- | --- | --- | --- |
|combine and rank everything|funct12_01_patent_ipc.sql |   |  
||funct12_02_join_all.sql |   |  
||funct12_03_join_all_ranked.sql |   |  

|script|what it does|comment|
|---|---|---|
| requirements.txt | for automatically installing all need Python libraries||
| my_pubmed_parser | pubmed parser from XXX with one small change by me||

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



