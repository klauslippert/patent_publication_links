create materialized view publ.names_pubmed_baseline
as
select 
    hash, 
	concat(author ->>'lastname',', ',array_to_string(regexp_split_to_array(author ->>'firstname',''),' ')) as authorname
from 
    (
        select 
            hash,
            json_array_elements(authors) as author 
            from publ.raw_pubmed_baseline
            where pubdate between to_timestamp('2000-01-01','YYYY-MM-DD') and to_timestamp('2007-12-31','YYYY-MM-DD')

    )a
;
