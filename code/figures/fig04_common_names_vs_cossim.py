

import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

env = os.environ
engine=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(env['PGUSER'],
                    env['PGPASSWORD'],env['PGHOST'],env['PGPORT'],env['PGDATABASE']),
                   poolclass=NullPool )
print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')


def human_format(num):
    #https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings-in-python/45846841
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.0f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])




sqlstring='''select 
                 no_intersect_names, 
                 cos_sim
             from publ.join_all
             where cos_sim is not null 
             --and delta_t > INTERVAL '122 days'
             --and (any_is_professor = True or applicant_university = True)
            ;'''
#join_tmp_raw_cossim 
df=pd.read_sql(sqlstring,engine)
print(len(df),'pairs total')

## group all no_intersect_names >= 10
df.loc[df['no_intersect_names']>=10,'no_intersect_names']=10

####################################
sqlstring = '''select no_intersect_names,  count(*) 
               from 
                   (
                       select 
                           no_intersect_names 
                       from publ.join_all
                       where cos_sim is not null  
                   )a
               group by no_intersect_names 
               order by no_intersect_names;'''
dfcnt=pd.read_sql(sqlstring,engine)

#                       --and delta_t > INTERVAL '122 days'
#                       --and (any_is_professor = True or applicant_university = True)

## group all no_intersect_names >= 10
dfcnt.loc[dfcnt['no_intersect_names']>=10,'no_intersect_names']=10
dfcnt = dfcnt.groupby('no_intersect_names').sum().reset_index()


#what is max number of intersecting names?
max_intersect_names = len(set(dfcnt['no_intersect_names']))
print('max_intersect_names',max_intersect_names)
########################################
## proc plot data
violin_data=[] 
x_liste=sorted(list(set(df['no_intersect_names'])))
print(x_liste)
for ii in x_liste:
    violin_data.append(df[df.no_intersect_names == ii]['cos_sim'].values)
 

fig=plt.figure(figsize=(14,8))
B=plt.boxplot(violin_data,positions=x_liste,
           medianprops=dict(color='black'),
           flierprops = dict(marker='.',markerfacecolor='gray', markeredgecolor='gray'),
           whis=[5,95])         #whis=[10,90]
            #whis='range')
  

#\n only scientific patents')

plt.ylim(-0.25,1)
#plt.xlim(0,max(x_liste)+2.5)
plt.xlim(0,max_intersect_names+2.5)

plt.grid(which='both',axis='y')
#plt.yticks([1e3,1e4,1e5])
plt.gcf().set_size_inches(10,4)
for xpos,txt in zip(dfcnt['no_intersect_names'],[human_format(x) for x in dfcnt['count']]):
    #print(xpos,txt)
    plt.text(xpos-0.15,-0.1,txt)
plt.text(max_intersect_names+0.5,-0.1,'total')   

plt.text(max_intersect_names+0.5,0,'no of pairs:') 


#threshold:
# taking the median of the lower whiskers boundary if no_intersect_names >= 2
whiskers_data = [item.get_ydata() for item in B['whiskers']]
lower_whiskers_boundary = [whiskers_data[x][1] for x in range(0,max_intersect_names*2,2)]
threshold = np.median(lower_whiskers_boundary[1:])
plt.hlines(threshold, 0.5,max_intersect_names+3,linestyles='dashed',colors='black') 

plt.text(max_intersect_names+0.5,threshold+0.015,'threshold')
plt.text(max_intersect_names+0.5,threshold-0.057,str(round(threshold,3)))


## number of pairs above threshold
sqlstring = f'''select 
                    no_intersect_names, 
                    count(*) 
                from 
                    (
                        select 
                            no_intersect_names 
                        from publ.join_all
                        where cos_sim is not null 
                        and cos_sim >={threshold} 
                    )a
                group by no_intersect_names order by no_intersect_names;'''
#    --and delta_t > INTERVAL '122 days'
#    --and (any_is_professor = True or applicant_university = True)

dfcnt2=pd.read_sql(sqlstring,engine)
## group all no_intersect_names >= 10
dfcnt2.loc[dfcnt2['no_intersect_names']>=10,'no_intersect_names']=10
dfcnt2 = dfcnt2.groupby('no_intersect_names').sum().reset_index()



for xpos,txt in zip(dfcnt2['no_intersect_names'],[human_format(x) for x in dfcnt2['count']]):
    #print(xpos,txt)
    plt.text(xpos-0.15,-0.2,txt)
plt.text(max_intersect_names+0.5,-0.2,'$\geq$ threshold')   

_=plt.gca().set_xticklabels(['$1$','$2$','$3$','$4$','$5$','$6$','$7$','$8$','$9$','$\geq$10'])
_=plt.gca().set_yticks([0,0.2,0.4,0.6,0.8,1])
_=plt.gca().set_yticklabels(['0.0','0.2','0.4','0.6','0.8','1.0'])

plt.xlabel('number of intersecting names')
#plt.ylabel('cos similarity (using BERT) of embedded MeSH terms \n using extraction from patent description and \n given publication MeSH terms')
#plt.title('patent - publication pairs by author names\n with patent filling date $\in$ [2000,2005] and article publication date $\in$ [2000,2007]\n and publication date > filling date')
plt.ylabel('cosine similarity')

figname='fig_common_names_vs_cossim.png'
plt.gcf().savefig(figname, dpi=200, bbox_inches="tight")
print(f'saved as: {figname}')
