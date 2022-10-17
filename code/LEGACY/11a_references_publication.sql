--drop materialized view publ.ref_pubmed_baseline;
create materialized view publ.ref_pubmed_baseline
as
with 
data_all as(
select * from (
select 
             data->>'pmid' as pmid_orig,
             data->>'doi' as doi
         from publ.stage_pubmed_baseline  
         --limit 500000
         ) x 
         where doi !=''
         
),
data_incl as (
select 
             hash,
             (json_array_elements(data->'references')) ->>'pmid' as pmid_ref  
         from publ.stage_pubmed_baseline   
         where hash in (select hash from publ.dist_publication)
         --limit 100000
)
select hash,array_agg(doi) as ref_doi from 
(
select incl.hash,compl.doi from 
(select * from data_all)compl 
join 
(select * from data_incl)incl
on incl.pmid_ref = compl.pmid_orig 
)a
group by hash
;
