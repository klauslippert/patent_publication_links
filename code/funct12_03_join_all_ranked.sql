drop materialized view if exists publ.join_all_ranked;
create materialized view publ.join_all_ranked
as 
with dd as (select *,
            case when any_is_professor is true or applicant_university is true then 0.1 
            else 0 end is_academic
            from publ.join_all 
            where delta_t between INTERVAL '182 days' and INTERVAL '548 days'
			and ('A61K' = any(ipc3)  or  'C12N' = any(ipc3)  or  'A61P' = any(ipc3)  or  'C07K' = any(ipc3)  or  'C07D' = any(ipc3)  or  'G01N' = any(ipc3)  or  'C12Q' = any(ipc3)  or  'C07H' = any(ipc3)  or  'C12P' = any(ipc3)  or  'C07C' = any(ipc3))
			),
	sure as ( select   0 as rank_number ,*
   				from dd
			where  (no_intersect_names >=3 or no_intersect_ref >=1)
        ),
     ranked as (
	select 
	case when cos_sim is not null and cos_sim >= 0.7 then 
	    RANK () OVER ( partition by patent_family 
		    	ORDER BY cos_sim+is_academic desc
		) 
		else 1000 end rank_number ,
	*
	from dd  
	),
	ranked_union_sure as (select * from ranked union all  select * from sure )
select * from ranked_union_sure where rank_number <=3

