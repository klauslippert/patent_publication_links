\echo PSQL: funct05_03_patent_master.sql - create MV publ.master_patente
---
drop materialized view if exists publ.master_patente
;
---
create materialized view publ.master_patente
as
select 
	xx.*,
	yy.applicant_university 
from 
	(
		select distinct
			patent_family,
    			proc as inventorname, 
	    		country,
    			is_professor,
    			date_filling,
    			extract(year from date_filling) as year_filling
		from publ.names_patente 
	) xx 
left join 
	(
		select 
			patent_family, 
			true=any(array_agg(distinct applicant_university)) as applicant_university
		from 
			(
				select 
					unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
					case when applicant ilike '%univ%' then true 
		     			     when applicant ilike '%hochschule%' then true
		     			     else false 
					end applicant_university
				from 
					(
						select 
							patent_no,
       							lower(unnest(xpath('/ep-patent-document/SDOBI/B700/B710/B711/snm/text()',data))::text) as applicant
						from publ.raw_patente
					) b 
			)c 
		group by patent_family
	)yy 
on xx.patent_family = yy.patent_family
;
---
create index on publ.master_patente (inventorname)
;

