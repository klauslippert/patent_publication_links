create materialized view if not exists patente.raw
as (
select hash,data
from (
select *, 
max(loaddate) over (partition by hash) as maxdate
                                from patente.stage
                         )a
                        where loaddate = maxdate                           
                        );
------------
create materialized view if not exists pubmed_baseline.raw
as (
select hash,data
from (
select *, 
max(loaddate) over (partition by hash) as maxdate
                                from pubmed_baseline.stage
                         )a
                        where loaddate = maxdate                           
                        );    
