import pandas as pd
import os
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine


print('load MeSH terms to database')

env=os.environ
engine=create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres',
                     poolclass=NullPool )
print(engine,'connection test:',pd.read_sql('select 1 as aa',engine)['aa'][0] ) 


MH  = pd.read_csv('/home/user/data/supplement/MH.TXT',
                  sep=';',
                  quotechar='|',
                  encoding='latin1',
                  header=None,
                  names=['id','term_german','term','subheadings']
                 ).drop(columns=['term_german','subheadings'])
print(f'loaded {len(MH)} datasets from file')

MH.to_sql('mesh_mainheadings',engine,schema='publ',if_exists='replace',index=False)

