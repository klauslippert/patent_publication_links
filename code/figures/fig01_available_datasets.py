
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
import matplotlib.pyplot as plt

env = os.environ
engine=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(env['PGUSER'],
                    env['PGPASSWORD'],env['PGHOST'],env['PGPORT'],env['PGDATABASE']),
                   poolclass=NullPool )
print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')

sqlstring='''with
pat_involved as (    select year_filling as year, count(*) as "patent families involved" from (
	select patent_family,year_filling from publ.master_patente 
	where patent_family in (select patent_family from publ.dist_patents)
	group by patent_family, year_filling ) a group by year_filling
	),
pat_total as (
    select year_filling as year, count(*) as "patent families total" from (
	select patent_family,year_filling from publ.master_patente 
	group by patent_family, year_filling ) a group by year_filling
	),
pub_involved as (	select pubyear as year , count(*) as "publications involved" from (
	select hash,pubyear from publ.master_pubmed_baseline 
	where hash in (select hash from publ.dist_publication)
	group by hash, pubyear ) a group by pubyear	
	),
pub_total as (	select pubyear as year , count(*) as "publications total" from (
	select hash,pubyear from publ.master_pubmed_baseline 
	group by hash, pubyear ) a group by pubyear	
	),
pub_both as (select a.*,b."publications involved" from 
	(select * from pub_total) a
	left join 
	(select * from pub_involved) b
	on a.year = b.year 
	),
pat_both as (select a.*,b."patent families involved" from 
	(select * from pat_total) a
	left join 
	(select * from pat_involved) b
	on a.year = b.year 
	)
select a.*,b."patent families total",b."patent families involved" from 
( select * from pub_both) a 
left join 
( select * from pat_both) b
on a.year = b.year 
order by year 
'''
df=pd.read_sql(sqlstring,engine)
df.index=[int(x) for x in df.year]
df=df.drop(columns=['year'])

## in thousand
for col in df.columns:
    df[col]=df[col]/1000




fi = df.plot(kind='bar',fill=True, edgecolor='black',
              color={"publications total": "gray", "publications involved": "gray",
                     "patent families total": "white", "patent families involved": "white"},
             width=0.7
             
            )


bars = fi.patches
patterns = [ '....','','....','']  # set hatch patterns in the correct order
hatches = []  # list for hatches in the order of the bars
for h in patterns:  # loop over patterns to create bar-ordered hatches
    for i in range(int(len(bars) / len(patterns))):
        hatches.append(h)
for bar, hatch in zip(bars, hatches):  # loop over bars and hatches to set hatches in correct order
    bar.set_hatch(hatch)
# generate legend. this is important to set explicitly, otherwise no hatches will be shown!
#plt.legend(bbox_to_anchor=(1.02,1),ncol=4)
plt.legend(ncol=2)
plt.xlabel('Patent-family: filling year / Publication: year of publication')
plt.ylabel('number documents (in thousand)')
plt.grid(which='both',axis='y')
#plt.title('available datasets')
plt.gcf().set_size_inches(10,4.5)

figname = 'fig_available_datasets.png'
plt.gcf().savefig(figname, dpi=200, bbox_inches="tight")

print(f'saved as: {figname}')
