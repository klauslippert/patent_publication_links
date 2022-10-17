--drop materialized view publ.ref_pubmed_baseline;
create table publ.ref_pubmed_baseline
as
with 
data_all as(
select 
             data->>'pmid' as pmid_orig,
             data->>'doi' as doi
         from pubmed_baseline.stage
         --limit 50000         
),
data_incl as (
select 
             hash,
             data->>'doi' as pub_doi,
             (json_array_elements(data->'references')) ->>'pmid' as pmid_ref  
         from pubmed_baseline.stage
         where hash in (select hash from publ.dist_publication)
         --limit 50000
)
select hash,
--case when trim(pub_doi) = '' then null
--else pub_doi end,   -> 201878
pub_doi,
array_agg(doi) as ref_doi from 
(
select incl.hash,incl.pub_doi,compl.doi from 
(select * from data_all)compl 
join 
(select * from data_incl)incl
on incl.pmid_ref = compl.pmid_orig 
)a
group by hash,pub_doi
;
