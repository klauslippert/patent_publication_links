import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd


def main():
    global engine
    env = os.environ
    engine=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(env['PGUSER'],
                    env['PGPASSWORD'],env['PGHOST'],env['PGPORT'],env['PGDATABASE']),
                   poolclass=NullPool )
    print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')

    ## create table for results
    _=create_kepat_raw()

    ## join patents and publications by inventor / author names
    myyears = [2000,2001,2002,2003,2004,2005]
    
    for myyear in myyears:
        
        before=get_nbr_sets()
        _=fire_query(createsqlstring(myyear))
        after=get_nbr_sets()
        print(f'found {after-before} name pairs for {myyear} vs [{myyear}, {myyear+1}, {myyear+2}]')

    print(f'found {get_nbr_sets()} name pairs in total')


def fire_query(sqlstring):
    connection = engine.connect()
    try:
        _ = connection.execute(sqlstring)
    except:
        print('ERROR')
        print(sqlstring)
    connection.close()

def create_kepat_raw():
    sqlstring=f'''create table publ.join_raw
                    (   patent_family text,
                        hash text,
                        pubdate timestamp,
                        date_filling timestamp,
                        delta_t interval,
                        no_intersect_names integer,
                        primary key (patent_family,hash)    
                    );'''
    _=fire_query(sqlstring)
    
def createsqlstring(myyear):
    sqlstring=f'''
        insert into publ.join_raw    
        select 
             patent_family,
             hash,
             pubdate,
             date_filling,
             pubdate-date_filling as delta_t,
             no_intersect_names 
        from 
             (            
                 select  
                     patent_family,
                     hash,
                     min(pubdate) as pubdate,
                     min(date_filling) as date_filling,
                     count(*) as no_intersect_names 
                 from 
                     (
                         select 
                             a.patent_family,
                             b.hash,
                             a.date_filling,
                             b.pubdate 
                         from             
                             (
                                 select 
                                     * 
                                 from publ.master_patente 
                                 where year_filling = {myyear}
                             )a
                         join
                             (
                                 select 
                                 * 
                                 from publ.master_pubmed_baseline 
                                 where pubyear = {myyear} 
                                 or pubyear = {myyear+1} 
                                 or pubyear = {myyear+2}
                             )b
                         on a.inventorname = b.authorname 
                     )c
                 group by patent_family,hash
             ) d 
         where pubdate > date_filling
         on conflict do nothing
         ;'''

    return sqlstring

def get_nbr_sets():
    rr=pd.read_sql('select count(*) from publ.join_raw',engine)['count'][0]
    return rr

if __name__ == '__main__':
    main()
