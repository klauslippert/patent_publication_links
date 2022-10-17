create materialized view publ.pat_ipc 
as 
select 
	patent_family, 
	array_agg(distinct ipc) as ipc_all,
	array_agg(distinct ipc[1]) as ipc1,
	array_agg(distinct array_to_string(ipc[1:2],'')) as ipc2, 
	array_agg(distinct array_to_string(ipc[1:3],'')) as ipc3 
	from 
		(
			select 
				array_to_string(regexp_matches(patent_no, '^EP[0-9]*'),'') as patent_family ,
				array[left(r1,1),right(left(r1,3),2),right(r1,1),r3[1],r3[2]] as ipc 
			from 
				(
					select 
						patent_no,
						r1,
						string_to_array(r2[1],'/')as r3  
					from 
						(
							select 
								patent_no , 
								r1[1],
								string_to_array(trim(array_to_string(r1[2:],' ')),' ') as r2 
							from 
								(		
									select 
										patent_no, 
										string_to_array(trim(array_to_string(xpath('/classification-ipcr/text/text()',unnest),' ')),' ')as r1 
									from 
										(				                 
											select  
												patent_no ,
												unnest(xpath('/ep-patent-document/SDOBI/B500/B510EP/classification-ipcr',data))
											from publ.raw_patente
										)a 
								) b 
						) c 
				)d 
		)e
	group by patent_family 
;
