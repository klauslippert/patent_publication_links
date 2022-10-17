create materialized view publ.master_pubmed_baseline
as 
select 
    distinct
    a.*,
    b.pubdate,
    b.pubyear
from 
    (
        select 
            hash,
            authorname,
            country_iso as country
        from publ.names_ext_pubmed_baseline
    ) a
    left join 
    (
        select 
            hash, 
            pubdate,
            extract(year from pubdate) as pubyear
        from publ.raw_pubmed_baseline
    ) b
    on a.hash=b.hash
;
create index on publ.master_pubmed_baseline (authorname);

