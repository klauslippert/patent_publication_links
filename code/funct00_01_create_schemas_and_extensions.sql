\echo PSQL: create extension pgcrypto
create extension if not exists pgcrypto;
---
\echo PSQL: create schema pubmed_baseline
create schema if not exists pubmed_baseline;
---
\echo PSQL: create schema patente
create schema if not exists patente;
---
\echo PSQL: create schema publ
create schema if not exists publ;
---
\echo PSQL: create schema functions
create schema if not exists functions;
--
\echo PSQL: create language plpython3u
create language plpython3u;
