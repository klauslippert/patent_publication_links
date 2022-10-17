create materialized view  publ.mesh_pubmed_baseline
as 
select 
    hash,
    string_agg(distinct mesh_term, ' '  order by mesh_term  ) as mh 
from 
    (
        select 
            hash, 
            --trim(v[1]) as mesh_id, 
            trim(v[2]) as mesh_term 
        from 
            (
                select 
                    hash, 
                    string_to_array(u,':') as v  
                from 
                    (
                        select 
                            hash,
                            unnest(string_to_array(mesh_terms,';'))as u 
                        from publ.raw_pubmed_baseline
                        where hash in (select * from publ.dist_publication)
                    )a
            )b 
    )c
group by hash
;
