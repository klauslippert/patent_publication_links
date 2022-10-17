create table publ.names3_pubmed_baseline
as
select  
hash,
authorname,
affiliation,
null as country_iso_text,
"ISO3166-1-Alpha-2" as country_iso_email
from 
(
 select 
                            *,
                            functions.emailending(affiliation) 
from publ.names2_pubmed_baseline
)e 
                    left join 
                    (
                        select 
                            * 
                        from publ.countrycodes
                    )f
                    on e.emailending = f."TLD"
;
