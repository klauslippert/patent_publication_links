\echo PSQL: funct05_01_patente_names.sql - create MV publ.names_raw_patente
--drop materialized view  publ.names_patente ;
--create materialized view  if not exists publ.names_raw_patente 
--(
--    patent_family text,
--    raw text,
--    country text,
--    date_filling timestamp,
--    PRIMARY KEY (patent_family,raw)
--)
--;
---
--\echo PSQL: insert into publ.names_raw_patente
---
create materialized view publ.names_raw_patente
as
    select 
        patent_family,raw,country,date_filling
    from 
        (
            select 
                unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
                raw,
                country,
                date_filling
            from 
                (
                    select 
                        patent_no, 
                        unnest(xpath('/ep-patent-document/SDOBI/B700/B720/B721/snm/text()',data))::text as raw,
                        unnest(xpath('/ep-patent-document/SDOBI/B700/B720/B721/adr/ctry/text()',data))::text as country,
                        date_filling
                    from 
                        (
                            select 
                                *,
                                to_timestamp(unnest(xpath('SDOBI/B200/B220/date/text()',data))::text,'YYYYMMDD') as date_filling
                            from
                            publ.raw_patente
                            --limit 1000
                        ) c
                    where c.date_filling between to_timestamp('2000-01-01','YYYY-MM-DD') and to_timestamp('2005-12-31','YYYY-MM-DD')
                )a 
            where raw is not null 
        ) b
    group by patent_family,raw,country,date_filling
--on conflict (patent_family,raw) do nothing
;
