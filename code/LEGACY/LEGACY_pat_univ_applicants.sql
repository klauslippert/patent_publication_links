create materialized view publ.pat_appl_univers
as
select patent_family, 
true=any(array_agg(distinct applicant_university)) as applicant_university,
true=any(array_agg(distinct inventor_professor)) as inventor_professor
from (
select unnest(regexp_matches(patent_no, '^EP[0-9]*')) as patent_family,
case when applicant like '%unive%' then true 
     else false end applicant_university,
case when inventor like '%prof%' then true 
     else false end inventor_professor 
from (
select patent_no,
       lower(unnest(xpath('/ep-patent-document/SDOBI/B700/B710/B711/snm/text()',data))::text) as applicant,
       lower(unnest(xpath('/ep-patent-document/SDOBI/B700/B720/B721/snm/text()',data))::text) as inventor
from (select * from publ.stage_patente   ) a 
) b 
)c 
group by patent_family
;

