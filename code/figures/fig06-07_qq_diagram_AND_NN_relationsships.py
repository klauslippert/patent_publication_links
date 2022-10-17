
import scipy.stats
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



what='ipc3'

sql=f'''select ipc , count(*) from (
select unnest({what}) as ipc from (
select distinct patent_family, any_is_professor, applicant_university,{what} from 
(select * from publ.join_all where {what} is not null
and ( any_is_professor is true or applicant_university is true)
) a ) b ) c 
group by ipc order by count desc '''
patents_academic_ipc = pd.read_sql(sql,engine)
#='ipc3'
#='ipc3'

sql=f'''select ipc , count(*) from (
select unnest({what}) as ipc from (
select distinct patent_family, any_is_professor, applicant_university,{what} from 
(select * from publ.join_all where {what} is not null
) a ) b ) c 
group by ipc order by count desc '''
patents_pairs_ipc = pd.read_sql(sql,engine)

sql=f'''select ipc, count(*) from 
(select unnest({what}) as ipc from publ.pat_ipc)a 
group by ipc order by count desc '''
patents_all_ipc = pd.read_sql(sql,engine)

sql=f'''select ipc, count(*) from (
select unnest({what}) as ipc from (
select distinct patent_family, {what},no_intersect_names, no_intersect_countries, no_intersect_ref from publ.join_all
where ipc3 is not null and 
((no_intersect_names >= 4 and no_intersect_countries >= 4 ) or 
no_intersect_ref >= 4 or cos_sim >= 0.95)
) a )b 
group by ipc order by count desc '''
patents_pairs_sure_ipc = pd.read_sql(sql,engine)



patents_academic_ipc['norm']=patents_academic_ipc['count'] / patents_academic_ipc['count'].sum()
patents_all_ipc['norm']=patents_all_ipc['count'] / patents_all_ipc['count'].sum()
patents_pairs_ipc['norm']=patents_pairs_ipc['count'] / patents_pairs_ipc['count'].sum()
patents_pairs_sure_ipc['norm']=patents_pairs_sure_ipc['count'] / patents_pairs_sure_ipc['count'].sum()


patents_ipc = patents_academic_ipc[['ipc','norm']].\
               merge(patents_all_ipc[['ipc','norm']],on='ipc',how='left').\
               reset_index().\
               rename(columns={'norm_x':'academic_pairs','norm_y':'all_EPO','index':'id'}).\
               merge(patents_pairs_ipc[['ipc','norm']],on='ipc',how='left').\
               rename(columns={'norm':'all_pairs'}).\
               merge(patents_pairs_sure_ipc[['ipc','norm']],on='ipc',how='left').\
               rename(columns={'norm':'sure_pairs'}).copy()

qq_pairs_sure = scipy.stats.probplot(patents_pairs_sure_ipc['norm'])
qq_all_epo = scipy.stats.probplot(patents_all_ipc['norm'])

qq_academic = scipy.stats.probplot(patents_academic_ipc['norm'])
qq_all_pairs = scipy.stats.probplot(patents_pairs_ipc['norm'])

#plt.yscale('log')
#plt.xscale('log')


plt.figure(figsize=(10,5))
plt.plot(qq_all_epo[0][0],qq_all_epo[0][1],'sk',label='all EPO patents')
plt.plot(qq_all_pairs[0][0],qq_all_pairs[0][1],'v',label='all patent-publication pairs',color='gray')
l1='''academic pairs: 'prof' in patent's inventor OR 'univ' in patent's applicant  '''
l2='''academic pairs'''
plt.plot(qq_academic[0][0],qq_academic[0][1],'o',label=l2,color='gray')
l1='''sure pairs: ("common names" >= 4 AND "common country" >= 4) OR "common references" >= 4 OR "cosine similarity" >= 0.95 '''
l2='sure pairs'
plt.plot(qq_pairs_sure[0][0],qq_pairs_sure[0][1],'ok',label=l2)

plt.xlabel('Theoretical quantiles')
plt.ylabel('ordered percentages of IPC classes in each subset')


### Text IPC class
xx=qq_pairs_sure[0][0][::-1]
yy=qq_pairs_sure[0][1][::-1]
txt=patents_pairs_sure_ipc['ipc']
for ii in range(10):
    plt.text(xx[ii]-0.01,yy[ii]+0.0075,txt[ii],rotation=90)
### Text IPC class
xx=qq_academic[0][0][::-1]
yy=qq_academic[0][1][::-1]
txt=patents_academic_ipc['ipc']
for ii in range(11):
    plt.text(xx[ii]-0.01,yy[ii]+0.0075,txt[ii],rotation=90)
    
plt.grid(which="major")
plt.xlim(1,3)
plt.ylim(-0.005,0.25)
plt.hlines(0.015,1,3)
plt.text(1.01,0.02,'threshold 1.5%')
#plt.legend(loc='upper left')
#plt.legend(loc='lower center', bbox_to_anchor=(0.5,-0.5),fontsize=12)
plt.legend(loc='upper left',fontsize=12)

#plt.title('Zoom into QQ diagram of IPC classes for different subsets')
#plt.show()



figname='fig_qq_diagram.png'
plt.gcf().savefig(figname, dpi=200, bbox_inches="tight")
print(f'saved as: {figname}')





##############################
## figure 07
##############################
sql_time_filter=''' delta_t between INTERVAL '182 days' and INTERVAL '548 days' '''
#############################################################################
allowed_ipc = patents_pairs_sure_ipc['ipc'][:10].to_list()
sql_ipc_filter = ' ('+' or '.join([f''' '{x}' = any(ipc3) ''' for x in allowed_ipc])+')'



sql=f'''select cnt_per_family, count(*) from (
select patent_family, count(*) as cnt_per_family from publ.join_all 
where {sql_time_filter} group by patent_family
) a 
group by cnt_per_family '''
pat_N_relations = pd.read_sql(sql,engine)
######################################################
sql=f'''select cnt_per_hash, count(*) from (
select hash, count(*) as cnt_per_hash from publ.join_all 
where {sql_time_filter} group by hash
) a 
group by cnt_per_hash '''
pub_N_relations = pd.read_sql(sql,engine)


sql=f'''select cnt_per_family, count(*) from (
select patent_family, count(*) as cnt_per_family from publ.join_all 
where {sql_time_filter} and {sql_ipc_filter} group by patent_family
) a 
group by cnt_per_family '''
pat_N_relations_ipc_filter = pd.read_sql(sql,engine)
######################################################
sql=f'''select cnt_per_hash, count(*) from (
select hash, count(*) as cnt_per_hash from publ.join_all 
where {sql_time_filter} and {sql_ipc_filter}  group by hash
) a 
group by cnt_per_hash '''
pub_N_relations_ipc_filter = pd.read_sql(sql,engine)



sql=f'''select cnt_per_family, count(*) from (
select patent_family, count(*) as cnt_per_family from publ.join_all_ranked
group by patent_family
) a 
group by cnt_per_family '''
pat_N_relations_ranked = pd.read_sql(sql,engine)
#--
sql=f'''select cnt_per_hash, array_agg(hash),count(*) from (
select hash, count(*) as cnt_per_hash from publ.join_all_ranked
group by hash
) a 
group by cnt_per_hash '''
pub_N_relations_ranked = pd.read_sql(sql,engine)


plt.figure(figsize=(10,5))
ms=20 #markersize
ls=14 #labelsize

common_label = f'''with delta publication date between 0.5 and 1.5 years'''
plt.scatter(pat_N_relations['cnt_per_family'], pat_N_relations['count'],
         marker='x',facecolors="red", edgecolors="red",s=ms,
         label=f'''1 patent : N publications {common_label}''')
plt.scatter(pub_N_relations['cnt_per_hash'], pub_N_relations['count'],
         marker='o',facecolors="coral", edgecolors="coral",s=ms,
         label=f'''1 publication : N patents {common_label}''')
###########################################
common_label = f'''like above + patent class filter'''
plt.scatter(pat_N_relations_ipc_filter['cnt_per_family'], pat_N_relations_ipc_filter['count'],
         marker='x',facecolors="black", edgecolors="black",s=ms,
         label=f'''1 patent : N publications {common_label}''')
plt.scatter(pub_N_relations_ipc_filter['cnt_per_hash'], pub_N_relations_ipc_filter['count'],
         marker='o',facecolors="grey", edgecolors="grey",s=ms,
         label=f'''1 publication : N patents {common_label}''')
#####
common_label = f'''like above + sure pairs + ranked via cosine similarity (Top 3)'''
plt.scatter(pat_N_relations_ranked['cnt_per_family'], pat_N_relations_ranked['count'],
            marker='x',facecolors="blue", edgecolors="blue",s=ms,
            label=f'''1 patent : N publications {common_label}''')
plt.scatter(pub_N_relations_ranked['cnt_per_hash'], pub_N_relations_ranked['count'],
            marker='o',facecolors="dodgerblue", edgecolors="dodgerblue",s=ms,
            label=f'''1 publication : N patents {common_label}''')


plt.xscale('log')
plt.yscale('log')

plt.grid(which="major")
plt.grid(which="minor")

plt.xlabel('N',fontsize=ls)
plt.ylabel('number of pairs',fontsize=ls)
plt.legend(loc='lower center', bbox_to_anchor=(0.5,-0.7),fontsize=ls)
plt.xticks(fontsize=ls)
plt.yticks(fontsize=ls)



#plt.show()
#plt.title('1:N relationships in patent-publication pairs',fontsize=ls)
figname='fig_NN_relationsships.png'
plt.gcf().savefig(figname, dpi=200, bbox_inches="tight")
print(f'saved as: {figname}')









