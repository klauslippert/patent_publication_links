create table publ.names3_pubmed_baseline
as
select 
    hash,
    authorname,
    affiliation,
    country_text,
    country_email,
    country_name,
    country_iso 
from 
    (
        select 
            *,
            case when country_text is not null then country_text 
                 when country_text is null and country_email is not null then country_email
            else null 
            end country_name 
        from 
            (
                select 
                    hash,
                    authorname,
                    affiliation,
                    country_text,
                    lower("CLDR display name") as country_email 
                from 
                    (
                        select 
                            hash,
                            authorname,
                            affiliation,
                            country_text[1],
                            functions.emailending(affiliation) 
                        from 
                            (
                                select 
                                    hash,
                                    authorname,
                                    affiliation,
                                    intersection(pub, countrylist) as country_text  
                                from 
                                    (
                                        select 
                                            * 
                                        from 
                                            (
                                                select 
                                                    *,
                                                    tsvector_to_array(to_tsvector('simple',affiliation)) as pub 
                                                from publ.names2_pubmed_baseline
                                            ) a ,
                                            (
                                                select 
                                                    array_agg(lower("CLDR display name")) as countrylist 
                                                from publ.countrycodes
                                            )b
                                    )c
                            )d 
                    )e 
                    left join 
                    (
                        select 
                            * 
                        from publ.countrycodes
                    )f
                    on e.emailending = f."TLD"
            )g 
        )h 
        left join
        (
            select 
                lower("CLDR display name"),
                "ISO3166-1-Alpha-2" as country_iso 
            from publ.countrycodes
        )i
        on h.country_name = i.lower
;
