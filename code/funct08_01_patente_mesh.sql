\echo PSQL: funct08_01_patente_mesh.sql - create MV publ.text_patente
---
create materialized view publ.text_patente
as
with
-- extract description and language from xml data
-- transform patent_no to patent_family
-- filter on patent_family which exist in the big JOIN
data1 as (          
            select 
                *   
            from 
                (
                    select 
                        patent_no,
                        unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
                        unnest(xpath('/ep-patent-document/description/@lang' ,data  ))::text as lang,
                        array_to_string(xpath('/ep-patent-document/description/p/text()' ,data  ),' ') as description
                    from publ.raw_patente 
                    --limit 1000
                ) a 
            where patent_family in (select patent_family from publ.dist_patents)
),
-- add a column with language priority info
data2 as ( 
            select 
                patent_family, 
                lang,
                case when lang = 'en' then 'a_'
                     when lang = 'de' then 'b_'
                     when lang = 'fr' then 'c_' 
                end as prio 
            from data1
         ),
-- group by patent_family         
data3 as (
            select  
                patent_family , 
                array_agg(distinct lang order by lang ) as lang 
            from 
                (
                    select  
                        patent_family, 
                        prio|| lang as lang 
                    from data2 
                )a 
            group by patent_family 
          ),
--                                
data4 as (
            select 
                patent_family, 
                right(lang[1],-2) as prio_lang  
            from data3 
         ),
-- get the desriptions again         
data5 as (
            select 
                a.*,
                b.patent_no,
                b.description,
                b.lang 
            from  
                (select * from data4)a 
                join 
                (select * from data1 )b
                on a.patent_family||a.prio_lang = b.patent_family||b.lang 
         )
-- group by patent_family, put togehter distinct descriptions and distinct languages  
select 
    patent_family,
    patent_no,
    lang[1] as lang,
    raw 
from 
    (		
        select 
            patent_family, 
            array_agg(patent_no) as patent_no,
            array_agg(distinct lang) as lang,
            string_agg(distinct description ,' ') as raw ,
            null as meshid
        from data5 
        group by patent_family
    ) c 
;
--ALTER TABLE publ.text_patente ADD COLUMN meshid text[];

