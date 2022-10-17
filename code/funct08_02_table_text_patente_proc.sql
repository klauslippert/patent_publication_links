\echo PSQL: funct08_02_table_text_patente_proc.sql - create T publ.text_patente_proc
---
create table if not exists publ.text_patente_proc
(
        patent_family text, 
        meshid text []
);
---
create index  if not exists idx_text_patente_proc on publ.text_patente_proc (patent_family);

