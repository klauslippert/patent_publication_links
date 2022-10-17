\echo PSQL: create MV publ.raw_pubmed_baseline
---
create materialized view publ.raw_pubmed_baseline  
as 
select 
	hash,
	data->>'abstract' as abstract,
	data->'authors' as authors,
	data->'chemical_list' as chemical_list,
	data->>'country' as country,
	data->>'delete' as delete,
	data->>'doi' as doi,
	data->>'issn_linking' as issn_linking,
	data->>'journal' as journal,
	data->'keywords' as keywords,
	data->>'medline_ta' as medline_ta,
	data->>'mesh_terms' as mesh_terms,
	data->>'nlm_unique_id' as nlm_unique_id,
	data->'other_id' as other_id,
	data->>'pmc' as pmc ,
	data->>'pmid' as pmid,
	to_timestamp(data->>'pubdate','YYYY-mm-dd') as pubdate,
	data->'publication_types' as publication_types,
	data->>'title' as title,
	data->'references' as references
from pubmed_baseline.raw
;
