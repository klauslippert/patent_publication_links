\echo PSQL: funct08_04_patente_mainheadings.sql - create MV publ.mesh_patente
---
create materialized view publ.mesh_patente
as 
select 
    patent_family, 
    string_agg(distinct term ,' ' order by term ) as mh  
from
    (
        select 
            patent_family,
            term  
        from 
            (
                select 
                    patent_family, 
                    unnest(meshid) 
                from publ.text_patente_proc
            ) a  
        left join
            (
                select 
                    * 
                from publ.mesh_mainheadings
            ) b 
        on a.unnest = b.id
    )c 
group by patent_family
;
