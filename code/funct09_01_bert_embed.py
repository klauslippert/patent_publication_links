import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
import multiprocessing as mp
import argparse
import torch
from sentence_transformers import SentenceTransformer


modelname = "bert-base-uncased"
sbert = SentenceTransformer(modelname)  






def main(args):
    ## do we embed publications or patents?
    global task
    global docid
    
    task = args.task
    print('working on data:',task)
    
    if task == 'pubmed_baseline':
        docid='hash'
    else:
        docid='patent_family'

    global engine
    env = os.environ
    engine=create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(env['PGUSER'],
                    env['PGPASSWORD'],env['PGHOST'],env['PGPORT'],env['PGDATABASE']),
                   poolclass=NullPool )
    print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')

 

    njobs=30
    mychunksize=100

    ## create table
    _=create_table()

    ## load data chunkwise
    sqlstring = f'''select {docid}, mh from publ.mesh_{task} ;'''
    dff=pd.read_sql(sqlstring,engine,chunksize=mychunksize)

    ## create bert vectors
    if njobs == 1:
        print(f'start single core mode')
        _ = [embed_one_df(dataset) for dataset in dff]
    else:
        print(f'start multi core mode: {njobs} cores')
        pool = mp.Pool(njobs)
        _ = pool.map(embed_one_df,[dataset for dataset in dff])
        pool.close()


def embed_one_df(thisdf):
    torch.set_num_threads(1)
    thisdf['embed']=[sbert.encode(x).tolist() if x != None else [] for x in thisdf['mh']]
    thisdf[[docid,'embed']].to_sql(f'embed_bert_{task}',engine,schema='publ',index=False,if_exists='append')
    return None

def create_table():
    sqlstring=f'''create table publ.embed_bert_{task} ({docid} text, embed float array  );
                  ALTER TABLE publ.embed_bert_{task}  ADD PRIMARY KEY ({docid});'''
    _=fire_query(sqlstring)

def fire_query(sqlstring):
    connection = engine.connect()
    try:
        _ = connection.execute(sqlstring)
    except:
        print('ERROR')
        print(sqlstring)
    connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(\
        description=f'''embed the MeSH main headings with BERT into vectors''',\
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--task",
                        choices=['pubmed_baseline','patente'],
                        dest='task',
                        required=True,
                        help="perform Bert embeddings on patents or on publications")
    args = parser.parse_args()
    main(args)






