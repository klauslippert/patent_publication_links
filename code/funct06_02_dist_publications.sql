\echo PSQL: funct06_02_dist_publications.sql - create MV publ.dist_publication
---
create materialized view publ.dist_publication
as 
select 
    distinct hash 
from publ.join_raw
;
CREATE INDEX ON publ.dist_publication (hash);
