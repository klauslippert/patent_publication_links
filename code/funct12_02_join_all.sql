create materialized view publ.join_all
as 
select e.*,f.ipc1,f.ipc2,f.ipc3 from 
(
	select 
	    c.*,
	    d.cos_sim 
	from 
	    (
	        select 
	            a.*,
	            b.no_intersect_ref 
	        from 
	            (
	                select patent_family,hash,
	                    pubdate,date_filling,delta_t ,
	                    no_intersect_names,no_intersect_countries,any_is_professor,
	                    applicant_university
	                from publ.join_raw 
	            ) a 
	            left join 
	            (
	                select 
	                    hash,
	                    patent_family,
	                    no_intersect as no_intersect_ref 
	                from publ.join_common_refs 
	            ) b 
	            on a.hash=b.hash 
	            and a.patent_family = b.patent_family
	    )c
	    left join
	        (
	            select 
	                * 
	            from publ.join_cos_sim
	        ) d 
	    on c.hash=d.hash 
	    and c.patent_family = d.patent_family
) e
left join
(select * from publ.pat_ipc) f
on e.patent_family = f.patent_family
;
