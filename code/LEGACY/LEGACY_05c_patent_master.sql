create materialized view publ.master_patente
as 
select distinct
    patent_family,
    proc as inventorname, 
    country,
    is_professor,
    date_filling,
    extract(year from date_filling) as year_filling
from publ.names_patente
;
create index on publ.master_patente (inventorname);
