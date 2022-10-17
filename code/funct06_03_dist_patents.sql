\echo PSQL: funct06_02_dist_patents.sql - create MV publ.dist_patents
---
create materialized view publ.dist_patents
as
select
    distinct patent_family
from publ.join_raw
;
CREATE INDEX ON publ.dist_patents (patent_family);
