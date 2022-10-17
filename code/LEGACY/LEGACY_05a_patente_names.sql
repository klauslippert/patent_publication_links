--drop table publ.names_patente ;
create table publ.names_patente 
(
    patent_family text,
    raw text,
    proc text default null,
    date_filling timestamp,
    PRIMARY KEY (patent_family,raw)
)
;
insert into publ.names_patente
    select 
        *
    from 
        (
            select 
                unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
                raw,
                null as proc,
                date_filling
            from 
                (
                    select 
                        patent_no, 
                        unnest(xpath('/ep-patent-document/SDOBI/B700/B720/B721/snm/text()',data))::text as raw,
                        date_filling
                    from 
                        (
                            select 
                                *,
                                to_timestamp(unnest(xpath('SDOBI/B200/B220/date/text()',data))::text,'YYYYMMDD') as date_filling
                            from
                            publ.stage_patente     
                            --limit 1000
                        ) c
                    where c.date_filling between to_timestamp('2000-01-01','YYYY-MM-DD') and to_timestamp('2005-12-31','YYYY-MM-DD')
                )a 
            where raw is not null 
        ) b
on conflict (patent_family,raw) do nothing
;
                
                 
