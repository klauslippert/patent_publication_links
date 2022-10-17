from collections import Counter
import re
import argparse 
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy import text as sqltxt
import os
import pandas as pd
import multiprocessing as mp

from elasticsearch import Elasticsearch

global es
es = Elasticsearch([{'host': '127.0.0.1', 'port': '9200'}])


global engine
env=os.environ
engine=create_engine('postgresql+psycopg2://postgres:postgres123@127.0.0.1:5432/postgres',
                     poolclass=NullPool )
print(engine,'connection test:',pd.read_sql('select 1 as aa',engine)['aa'][0] )  


def main(args):
    

    
    
    mychunksize=100
    njobs=30

    
    sqlstring = f'''select hash,affiliation,authorname from publ.names2_pubmed_baseline 
                    where affiliation is not null 
                    and country is null ;'''
    
    dff=pd.read_sql(sqlstring,engine,chunksize=mychunksize)
    
    #print(dff.head())
    
    
    #_=process_upload_one_df(dff)
    if njobs == 1:
        print(f'start single core mode')
        _ = [process_upload_one_df(df) for df in dff]
        
    else:
        print(f'start multi core mode: {njobs} cores')
        pool = mp.Pool(njobs)
        _ = pool.map(process_upload_one_df,[df for df in dff])
        pool.close() 

def process_upload_one_df(df):
    """ getting the country via querying 
        the affiliation at elasticsearch API 
        with ror.org data dump
    """
    res=[]
    for term,identifier,author in zip(df['affiliation'],df['hash'],df['authorname']):
        res.append(extended_query_local(term,identifier,author))

    res2=pd.DataFrame(res,columns=['identifier','authorname','orig','norm','countryname','country'])    
    #print(res2)
    
    for thisidentifier,   thiscountry,thisname in zip(res2['identifier'],res2['country'],res2['authorname']):
         sqlstring = f'''update publ.names2_pubmed_baseline set country = '{thiscountry}' 
                         where hash  = '{thisidentifier}'
                         and authorname = '{proc_sqlstring(thisname)}'
                         ; '''
         try:     
             #print(sqlstring)
             connection = engine.connect()         
             connection.execute(sqltxt(sqlstring))
             _=connection.close()       
         except:
             print('ERROR: ',sqlstring)
    
def get_email_ending(text):
    ## from https://emailregex.com/
    expr='''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''
    a=re.search(expr,text)
    if a:
        email = text[a.span()[0]:a.span()[1]]
        ending=email.split('.')[-1]
    else:
        ending=''
    return ending.upper()


def extended_query_local(termsorig,identifier,author):
    term = termsorig.replace('Student','')
    my_query = {"query": {"match": {"name": term }}}
    tmp=es.search(index="ror", body=my_query)['hits']['hits'][:3]
    r=[]
    for tt in tmp:
        r.append((term,
                  tt['_source']['name'],
                  tt['_source']['country']['country_name'],
                  tt['_source']['country']['country_code'],
                  tt['_source']['addresses'][0]['city'],
                  get_email_ending(term)
                ))
    res = pd.DataFrame(r,columns=['orig','norm','country','country_code','city','emailend']) 
    res['country_inside']=[True if re.search(x.lower(),y.lower()) else False for x,y in zip(res['country'],res['orig'])  ]
    res['city_inside']=[True if re.search(x.lower(),y.lower()) else False for x,y in zip(res['city'],res['orig'])  ]
    res['email_fits']=[True if x==y else False for x,y in zip(res['emailend'],res['country_code'])  ]
    res['cat_true']=[[x,y,z] for x,y,z in zip(res['country_inside'],res['city_inside'],res['email_fits'])]
    res['cnt_true']=[Counter(x)[True] for x in res['cat_true']]
    result = res.sort_values('cnt_true',ascending=False).reset_index(drop=True).iloc[0]
    #print(result)
    return (identifier,author,termsorig,result['norm'],result['country'],result['country_code'])

def proc_sqlstring(sqlword):
    sqlword = sqlword.replace("'","''")
    sqlword = sqlword.replace(':','\:')
    return sqlword


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'''
    enrich publication names with country codes by:
        
    getting the country via querying 
    the affiliation at elasticsearch API 
    with ror.org data dump
    ''', formatter_class=argparse.RawTextHelpFormatter)
    
    #parser.add_argument("--lang",
    #                    dest='lang',
    #                    choices=['en','de','fr'],
    #                    required=True,
    #                    help="which language")  
    
    args = parser.parse_args()
    
    main(args)
