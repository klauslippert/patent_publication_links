\echo PSQL: create UDF function for cosine similarity
---
create language plpython3u;
---
drop function if exists functions.vec_sim;
---
CREATE FUNCTION functions.vec_sim(invec1 double precision[], invec2 double precision[])
 RETURNS double precision
 LANGUAGE plpython3u
 PARALLEL SAFE
AS $function$
from scipy import spatial
if invec1 and invec2:
    cossim=1-spatial.distance.cosine(invec1,invec2)
else:
    cossim = -1 
return cossim
$function$
;
------------------------------------------------
\echo PSQL: create materialized view.publ_join_cos_sim
---
create materialized view publ.join_cos_sim
as
select 
    c.patent_family,
    c.hash,
    case 
        when c.embed_publ is null or d.embed is null then null 
        else functions.vec_sim(c.embed_publ,d.embed) 
    end cos_sim
from
    (
        select 
            a.patent_family, 
            a.hash, embed as embed_publ 
            from 
                (
                    select 
                        patent_family,
                        hash from 
                    publ.join_raw 
                    --limit 100 
                )a 
                left join 
                (
                    select 
                        * 
                    from publ.embed_bert_pubmed_baseline
                )b
                on a.hash = b.hash
    ) c 
    left join 
    (
        select 
            * 
        from publ.embed_bert_patente
    )d 
    on c.patent_family = d.patent_family
;
