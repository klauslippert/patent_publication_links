create table publ.tmp_text_patente
as 
select a.patent_family,a.patent_no,a.lang,a.raw,b.meshid from                      
(select * from publ.text_patente)a 
join 
(select * from pat_core."text")b 
on a.patent_family = b.patent_family 
;

--test
--select count(*) from publ.tmp_text_patente   --316278
--select count(*) from publ.text_patente   --316278

drop table publ.text_patente;
ALTER TABLE publ.tmp_text_patente RENAME TO text_patente;
