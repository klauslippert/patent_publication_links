import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import pandas as pd
import personnamenorm
import multiprocessing as mp

def main():
    global engine
    env = os.environ
    engine=create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres',
                     poolclass=NullPool )

    print(f'''DB connection: {engine}   connection-test {pd.read_sql('select 1 as cnt',engine)['cnt'][0]}''')

    print('funct05_02_process_patent_names.py - processing of the patent inventor names')
    
    ## TODO das sollte in eine environment variable ausgelagert werden..
    ##      mit besseren default werten.. 
    mychunksize = 1000
    njobs=20

    ## create empty table to fill
    sqlstring='''CREATE TABLE publ.names_patente (
        patent_family TEXT,
        raw TEXT,
        country TEXT,
        date_filling TIMESTAMP WITH TIME ZONE,
        proc TEXT,
        is_professor BOOLEAN
        );
        '''
    with engine.connect() as con:
        con.execute(sqlstring)


    ## do the processing
    _=proc_author(mychunksize, njobs)
    
#legacy
#def proc_sqlstring(sqlword):
#    sqlword = sqlword.replace("'","''")
#    sqlword = sqlword.replace(':','\:')
#    return sqlword

def proc_name(df):
    ## initialize the name normalization library
    pnn=personnamenorm.namenorm(debug=False)

    ## process the names
    proc=[]
    is_professor=[]
    for thisname in df['raw'].to_list():
        try:
            pnn.unify(thisname)
            tmp = [False if y==-1 else True for y in [x.lower().find('prof') for x in pnn.name['title']]]
            is_professor.append(any(tmp))
            proc.append(pnn.name['fullname_abbrev'])
        except:
            print(f'problem with processing of {thisname} -> take it as processed name')
            proc.append(thisname)
            is_professor.append(False)
    df['proc']=proc
    df['is_professor']=is_professor

    ## upload to db

    df.to_sql('names_patente',engine,schema='publ', if_exists='append',index=False)


def proc_author(mychunksize, njobs):
    ## read un-processed data from database
    dff = pd.read_sql(f'''select * from publ.names_raw_patente;''',
                      engine, chunksize=mychunksize)

    if njobs == 1:
        print('start single core mode')
        _ = [proc_name(chunk) for chunk in dff]
    else:
        print(f'start multi core mode: {njobs} cores')
        pool = mp.Pool(njobs)
        _ = pool.map(proc_name,[chunk for chunk in dff])
        pool.close()

if __name__ == '__main__':
    main()
