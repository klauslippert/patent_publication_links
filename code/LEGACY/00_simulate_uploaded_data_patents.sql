create materialized view publ.stage_patente as 
select patent_no,data,loaddate,hash from (
select *,
     to_timestamp(unnest(xpath('/ep-patent-document/@date-publ',data))::text,'YYYYMMDD') as date_publ
from pat_stage.data )a 
where   date_publ >= to_timestamp('2000-01-01','YYYY-MM-DD') 
;

