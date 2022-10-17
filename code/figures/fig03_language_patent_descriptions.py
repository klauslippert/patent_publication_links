import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
import matplotlib.pyplot as plt

###
env = os.environ
engine=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(env['PGUSER'],
                    env['PGPASSWORD'],env['PGHOST'],env['PGPORT'],env['PGDATABASE']),
                   poolclass=NullPool )
print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')
###


sqlstring = '''
with dd as (
select lang, year_filling, count(*)
from (
select a.*,b.year_filling  from 
(select patent_family,lang from publ.text_patente)a 
left join 
(select patent_family,year_filling from publ.master_patente group by patent_family,year_filling)b
on a.patent_family = b.patent_family
)c
group by lang, year_filling 
),
a as (select year_filling as year, count as english from dd where lang ='en') , 
b as (select year_filling as year, count as german from dd where lang ='de'),
c as (select year_filling as year, count as french from dd where lang ='fr'),
d as (select a.*,b.german from a left join b on a.year=b.year) 
select * from (select d.*,c.french from d left join c on d.year=c.year)e order by year;
'''
df=pd.read_sql(sqlstring,engine)
df.index=[int(x) for x in df.year]
df=df.drop(columns=['year'])
####

fi = df.plot(kind='bar',fill=True, edgecolor='black',
              color="white",
             width=0.6
             
            )


bars = fi.patches
patterns = [ '....','','////']  # set hatch patterns in the correct order
hatches = []  # list for hatches in the order of the bars
for h in patterns:  # loop over patterns to create bar-ordered hatches
    for i in range(int(len(bars) / len(patterns))):
        hatches.append(h)
for bar, hatch in zip(bars, hatches):  # loop over bars and hatches to set hatches in correct order
    bar.set_hatch(hatch)
# generate legend. this is important to set explicitly, otherwise no hatches will be shown!
plt.legend(bbox_to_anchor=(1.02,1))
plt.ylabel('number of patent families')
plt.xlabel('patent filling year')
plt.title('languages of patent description used for MeSH extraction')

#plt.yscale('log')
plt.grid(which='both',axis='y')
#plt.yticks([1e3,1e4,1e5])
plt.gcf().set_size_inches(10,4)



plt.gcf().set_size_inches(10,4)

figname='fig_languages_patent_description.png'
plt.gcf().savefig(figname, dpi=200, bbox_inches='tight')
print(f'saved as: {figname}')



