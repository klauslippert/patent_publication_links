\echo PSQL: create materialized view publ.journalnormalize
---
CREATE SEQUENCE seq_j_id;
---
create materialized view if not exists publ.journal_normalize 
as 
with 
data as (select * from publ.raw_pubmed_baseline ),
uniondata as (select 
		      distinct * 
		      from (
                                select distinct 
                                   regexp_replace(lower(medline_ta), '[^a-z0-9]+', '','g')   as abbrev,
                                   journal as fullname 
                                from data 
     				union all 
	    			select distinct 
                                     regexp_replace(lower(journal), '[^a-z0-9]+', '','g') as abbrev,
                                     journal as fullname  
                                from data
		    		) a 
		      where abbrev !=''
		  )	
select abbrev,
       array_agg(fullname) as agg_fullname ,
      'journalid'||nextval('seq_j_id') as journal_id 
      from uniondata
      group by abbrev 
;
