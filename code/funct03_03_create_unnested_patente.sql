\echo PSQL: funct03_03_create_unnested_patente.sql - create MV publ.raw_patente
--
create materialized view publ.raw_patente
as
select
unnest(xpath('/ep-patent-document/@id',data))::text as patent_no,
data,hash
from patente.raw
;
