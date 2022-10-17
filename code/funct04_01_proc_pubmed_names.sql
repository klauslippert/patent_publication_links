\echo PSQL: create MV publ.names_pubmed_baseline
---
create materialized view publ.names_pubmed_baseline  
as
with 
cc as (
    select 
        * 
    from 
        (
        select 
                    hash, 
                    concat(author ->>'lastname',', ',array_to_string(regexp_split_to_array(author ->>'firstname',''),' ')) as authorname,
                    case 
                        when trim(author ->> 'affiliation') ='' then null 
                        else author ->> 'affiliation' 
                    end affiliation
        from 
            (
                select 
                    hash,
                    doi,
                    json_array_elements(authors) as author 
                from publ.raw_pubmed_baseline 
                where pubdate between to_timestamp('2000-01-01','YYYY-MM-DD') and to_timestamp('2007-12-31','YYYY-MM-DD')
                --limit 1000
            )a
        ) b 
    where trim(authorname) != ','
),
dd as (
    select 
        a.*,
        case 
            when b.no_aff_per_hash is not null then b.no_aff_per_hash
            else 0 
        end as no_aff_per_hash
	from 
        (
            select 
                * 
            from cc 
        )a
        left join 
        (
            select 
                hash,
                array_length(array_remove(array_agg(affiliation),null),1)  as no_aff_per_hash
            from cc 
            group by hash   
        ) b 
        on a.hash = b.hash 
),
ee as (
	select 
        hash, 
        array_agg(authorname) as authors ,
        case 
            when no_aff_per_hash = 1 then array_remove(array_agg(affiliation),null) 
            else array_agg(affiliation) 
        end as aff,
	    no_aff_per_hash
	from dd 	
	group by hash, no_aff_per_hash
),
ff as (
    select 
        hash, 
        no_aff_per_hash, 
        unnest(authors) as authorname ,
        unnest(affil) as affiliation 
    from 
        (
            select 
                hash, 
                no_aff_per_hash,
                authors,
                case 
                    when no_aff_per_hash = 1 then array_fill(aff[1], array[array_length(authors,1)])
                    else aff 
                end as affil 
            from ee 
        ) a 
)
select 
    hash, 
    no_aff_per_hash, 
    authorname, 
    affiliation,
    "ISO3166-1-Alpha-2" as country_email
from 
    (
        select 
            *,
            functions.emailending(affiliation)  
        from ff
    ) e 
    left join 
    (
        select 
            * 
        from publ.countrycodes
    )f
    on e.emailending = f."TLD"
;
