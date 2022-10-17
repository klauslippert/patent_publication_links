CREATE OR REPLACE FUNCTION functions.array_intersect(anyarray, anyarray)
 RETURNS anyarray
 LANGUAGE sql
AS $function$
    SELECT ARRAY(
        SELECT UNNEST($1)
        INTERSECT
        SELECT UNNEST($2)
    );
$function$
;
---
create materialized view publ.join_common_refs
as
select 
    hash,
    patent_family,
    ref_patents,
    ref_pub ,
    case 
        when no_tmp is null and ref_patents is not null and ref_pub is not null then 0  
        when no_tmp is not null then no_tmp  
        else null  
    end no_intersect 
from 
    (
        select 
            *,
            array_length(functions.array_intersect(ref_patents,ref_pub),1) as no_tmp 
        from 
            (
                select 
                    c.*,
                    d.ref_doi as ref_pub 
                from 
                    (
                        select 
                            a.*,
                            b.ref_patents 
                        from 
                            (
                                select 
                                    hash,
                                    patent_family 
                                from publ.join_raw
                            ) a 
                        left join 
                            (
                                select 
                                    patent_family, 
                                    array_agg(distinct crossref_doi) as ref_patents 
                                from publ.ref_raw_patents
                                where crossref_doi is not null 
                                group by patent_family 
                            )b 
                        on a.patent_family = b.patent_family
                    )c 
            left join 
                (
                    select 
                        * 
                    from publ.ref_pubmed_baseline 
                ) d 
            on c.hash = d.hash 
        )d
    )e 
;
