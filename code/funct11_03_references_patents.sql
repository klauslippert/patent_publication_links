create table publ.ref_raw_patents
as 
select 
    patent_no,
    pub_refid,
    patent_family,
    array_to_string(author,'  ') as author,
    article_title,
    serial_title,
    serial_pubyear,
    y.agg_fullname[1] as serial_title_full,
    null as crossref_doi
from 
    (
        select 
            *,
            REGEXP_REPLACE(lower(serial_title),'[^a-z0-9]+', '','g') as serial_title_abbrev   
        from 
            (
                select 
                    patent_no,
                    unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
                    (xpath('/li/nplcit/@id',tt))[1]::text as pub_refid ,
                    xpath('/li/nplcit/article/author/name/text()',tt) as author, 
                    (xpath('/li/nplcit/article/atl/text()',tt))[1]::text as article_title, 
                    (xpath('/li/nplcit/article/serial/sertitle/text()',tt))[1]::text as serial_title,
                    left((xpath('/li/nplcit/article/serial/pubdate/sdate/text()',tt))[1]::text,4) as serial_pubyear
                from 
                    (
                        select 
                            patent_no,
                            unnest(xpath('/ep-patent-document/ep-reference-list/p/ul/li',data )) as tt 
                        from publ.raw_patente 
                        --limit 100 offset 1000
                    ) aa 
            ) bb 
        where pub_refid is not null 
        and patent_family in (select patent_family from publ.dist_patents)
    ) x 
    left join
    (
        select 
            * 
        from publ.journal_normalize 
    ) y 
    on x.serial_title_abbrev = y.abbrev
;
    
    

---  fill journal titles where the normalization didn't work
update publ.ref_raw_patents set serial_title_full = serial_title where serial_title_full is null;
--- this should go next time directly into the table.. I forgot -> doing it now
alter table publ.ref_raw_patents add column querystring text;
update publ.ref_raw_patents set querystring= trim(concat(author,' ',article_title,' ',serial_pubyear,' ',serial_title_full));




