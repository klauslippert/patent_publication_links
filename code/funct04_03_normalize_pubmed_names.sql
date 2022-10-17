create materialized view publ.names_ext_pubmed_baseline
as
select hash, authorname,
affiliation, no_aff_per_hash,
country_email,country_text,
case when trim(country_text) = '' and country_email is not null  then country_email
 when country_text is null and country_email is not null  then country_email 
else country_text 
end as country_iso
from 
(select a.*,b.country_text from 
(select * from publ.names_pubmed_baseline ) a 
left join 
(select * from publ.tmp_extract_country_iso) b 
on a.affiliation = b.affiliation
) c
;
