#!/bin/bash


## put in your own email here !
export myemail=youremail@example.com
##


source ./db_credentials.sh

function main {
echo "##" `date` "start complete pipeline"

source db_credentials.sh

#00_prepare_db
#01_get_data_pubmed_baseline
#02_get_data_patents
#03_create_raw_data
#04_preprocess_pubmed_baseline
#05_preprocess_patents
#06_create_publication_patent_pairs
#07_postprocess_publication
#08_postprocess_patents
#09_embed_with_bert
#10_create_cosine_similarities
#11_create_common_references
#12_create_final_results
13_create_figures

}


function 00_prepare_db {
psql -f funct00_01_create_schemas_and_extensions.sql
psql -f funct00_02_SQL_functions.sql
python3 funct00_03_upload_MeSH_mainheadings.py
python3 funct00_04_countrycodes_for_emailendings.py
python3 funct00_05_countrynames_for_keywordextraction.py
}

function 01_get_data_pubmed_baseline {
echo "##" `date` "download pubmed baseline data and upload to postresql"
python3 funct01_01_data_download_pubmed.py
}

function 02_get_data_patents {
echo "##" `date` "download patent data and upload to postgresql"
python3 funct02_01_data_download_epo.py
python3 funct02_02_create_patent_filelist.py > patentfiles
psql -f funct02_03_create_table_patent_stage.sql
./funct02_04_patent_xml_upload.sh
}

function 03_create_raw_data {
echo "##" `date` "create distinct datasets for patents and publications"
psql -f funct03_01_create_pub_pat_raw.sql
echo "##    -> patente.raw"
echo "##    -> pubmed_baseline.raw"
echo "##" `date` "some un-nesting of publication data"
psql -f funct03_02_create_unnested_pubmed_baseline.sql
psql -f funct03_03_create_unnested_patente.sql
}

function 04_preprocess_pubmed_baseline {
##  - creates raw data out of staging data
##  - normalisation of the author names, 
##    filtered by publication year: [2000-01-01 ... 2007-12-31]
##  - create a master table for the JOIN by adding publication dates
    echo "##" `date` "process pubmed baseline data"
        echo "##    " `date` "create materialized view with raw data  -> create publ.raw_pubmed_baseline"
        psql -f funct04_01_proc_pubmed_names.sql
        python3 funct04_02_country_extract.py
        psql -f funct04_03_normalize_pubmed_names.sql
        echo "##    " `date` "create materialized view for the JOIN -> create publ.master_pubmed_baseline" 
        psql -f funct04_04_pubmed_master.sql
}


function 05_preprocess_patents {
##  - normalisation of the inventor names, 
##    grouped by the patent-family,
##    filtered by the filling year: [2000-01-01 ... 2005-12-31]
    echo "################################"
    echo "##" `date` "process patent data"
    psql -f funct05_01_patente_names.sql
    echo "##" `date`
    python3 funct05_02_process_patent_names.py
    echo "##" `date`
    psql -f funct05_03_patent_master.sql
}

function 06_create_publication_patent_pairs {
##  - JOIN of publications and patents, done year by year
##    filtered by "publication date > patent filling date"
    echo "##" `date` "create publication patent pairs -> publ.join_raw"
    python3 funct06_01_join_patent_publication.py
    echo "##" `date` "which publications are involved -> publ.dist_publication"
    psql -f funct06_02_dist_publications.sql
    echo "##" `date` "which patents are involved -> publ.dist_patents"
    psql -f funct06_03_dist_patents.sql
}

 

function 07_postprocess_publication {
##  - MeSH terms for the publications
##    filterd by occurence in the result of the JOIN

    echo "##" `date` "07_postprocess publication"
        echo "##    " `date` "extract MeSH from pubmed baseline -> create publ.mesh_pubmed_baseline"
        psql -f funct07_01_pubmed_mesh.sql
}


function 08_postprocess_patents {
    ##  * create table with descriptions from patent families
    ##    which occur in the result of the JOIN
    ##    only one language by patent family, priortized by "english", "german", "french"
    ##  * extract MeSH terms from those patent descriptions and provide english mainheadings
    echo "##" `date` "08_postprocess patents"
        echo "##    " `date` "prepare patent descriptions -> publ.text_patente" 
        psql -f funct08_01_patente_mesh.sql
        psql -f funct08_02_table_text_patente_proc.sql

        echo "##    " `date` "extract MeSH IDs from english descriptions"
        python3 funct08_03_MeSH_extract.py --lang en
        echo "##    " `date` "extract MeSH IDs from german descriptions"
        python3 funct08_03_MeSH_extract.py --lang de
        echo "##    " `date` "extract MeSH IDs from french descriptions"
        python3 funct08_03_MeSH_extract.py --lang fr

        echo "##    " `date` "transform MeSH IDs to MeSH mainheadings -> publ.mesh_patente"
        psql -f funct08_04_patente_mainheadings.sql
}

function 09_embed_with_bert {
    ##  - create embeddings for each document
    echo "##" `date` "09_embed_with_bert"
        echo "##    " `date` "create embeddings for publications -> publ.embed_bert_pubmed_baseline"
        python3 funct09_01_bert_embed.py --task pubmed_baseline
        echo "##    " `date` "create embeddings for patents -> publ.embed_bert_patente"    
        python3 funct09_01_bert_embed.py --task patente

        
}


function 10_create_cosine_similarities {
    echo "##" `date` "create cosine similiarities -> publ.join_cos_sim"
        psql -f funct10_01_join_cosine_similarity.sql

}




function 11_create_common_references {
    echo "##" `date` "create common references"
        echo "##    " `date` "create table for journal normalisation -> publ.journal_normalize"
#        psql -f funct11_01_create_journalnorm_table.sql
        echo "##    " `date` "create publication references -> publ.ref_pubmed_baseline"
#        psql -f funct11_02_references_publication.sql
        echo "##    " `date` "create patent references -> publ.ref_patents"
#        psql -f funct11_03_references_patents.sql
        echo "##    " `date` "enrich patent references with crossref"
        python3 funct11_04_enrich_patents_w_crossref.py --email $myemail
        echo "##    " `date` "find common references"
        psql -f funct11_05_common_references.sql

}

function 12_create_final_results {
    echo "##" `date` "create final results"
    psql -f funct12_01_patent_ipc.sql
    psql -f funct12_02_join_all.sql 
    psql -f funct12_03_join_all_ranked.sql 
    
    
}

function 13_create_figures {
    echo "##" `date` "create figures for publication"
        cd /home/user/code/figures
        python3 fig01_available_datasets.py
        python3 fig03_language_patent_descriptions.py  
        python3 fig04_common_names_vs_cossim.py             
        python3 fig05_common_references_vs_cossim.py
        python3 fig06-07_qq_diagram_AND_NN_relationsships.py
        cd /home/user/code
        mv /home/user/code/figures/*png /home/user/data/figures
        
        
}


main
echo "##" `date` "done"
