import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd


def main():
    print('funct06_01_join_patent_publication.py - joining patent and publications by names')

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
                        intersect_names text[],
                        intersect_countries text[],
                        no_intersect_countries integer,
                        is_professor boolean[],
                        any_is_professor boolean,
                        applicant_university boolean,
                        primary key (patent_family,hash)    
                    );'''
    _=fire_query(sqlstring)
    
def createsqlstring(myyear):
    sqlstring=f'''
        insert into publ.join_raw    
        with
        d_pat as (select * from publ.master_patente 
                  where country is not null and year_filling = {myyear}
                 ),
        d_pub as (select * from publ.master_pubmed_baseline
                   where pubyear = {myyear} or pubyear = {myyear+1} or pubyear = {myyear+2}
                 ),
        join_incl_country as (select a.patent_family, b.hash, a.inventorname ,
                                     a.is_professor,a.applicant_university,
                                     a.country, a.date_filling, b.pubdate
                              from 
                              (select * from d_pat ) a 
                              join  
                              (select * from d_pub where country is not null)b 
                              on a.inventorname = b.authorname  and a.country = b.country
                             ) ,
        join_no_country as (select a.patent_family, b.hash, a.inventorname ,
                                   a.is_professor,a.applicant_university,
                                   a.country, a.date_filling, b.pubdate
                            from 
                            (select * from d_pat ) a 
                            join  
                            (select * from d_pub where country is  null)b 
                            on a.inventorname = b.authorname  
                           ) ,
        join_all as ( select * from 
                        (select * from join_incl_country 
                         union all 
                         select * from join_no_country
                        )a 
                      where pubdate > date_filling
                     )
        select patent_family,hash,pubdate,date_filling,pubdate-date_filling as delta_t,
               no_intersect_names,intersect_names,intersect_countries,
               array_length(intersect_countries,1) as no_intersect_countries,is_professor,
               true = any(is_professor) as any_is_professor,
               true = any(applicant_university) as applicant_university
        from (
                select  
                     patent_family,
                     hash,
                     min(pubdate) as pubdate,
                     min(date_filling) as date_filling,
                     count(*) as no_intersect_names,
                     array_agg(inventorname) as intersect_names,
                     array_agg(country) as intersect_countries,
                     array_agg(is_professor) as is_professor,
                     array_agg(applicant_university) as applicant_university
                from  join_all
                group by patent_family, hash 
              ) x 
        on conflict do nothing
         ;'''

    return sqlstring

## nbr of patent-publication pairs
    ## old version w/o countries: 89.771.826 
    ## dist publication 2.189.757
    ## dist patente 580.710

    ## new version w/  countries: 52.595.892
    ## dist publication 1.490.940
    ## dist patente 516.809

def get_nbr_sets():
    rr=pd.read_sql('select count(*) from publ.join_raw',engine)['count'][0]
    return rr

if __name__ == '__main__':
    main()
