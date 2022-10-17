from keyword_extraction import DictLU_Extract_Exact
import argparse 
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy import text as sqltxt
import os
import pandas as pd
import pickle
import multiprocessing as mp

global engine
env=os.environ
engine=create_engine('postgresql+psycopg2://postgres:postgres123@127.0.0.1:5432/postgres',
                     poolclass=NullPool )
print(engine,'connection test:',pd.read_sql('select 1 as aa',engine)['aa'][0] )  


def main(args):
    

    global DEE 

    
    
    filename = 'country_name_iso_dict.p'
    print(f'loading MeSH data from {filename}')
    try:
        [dicts_lower,dicts_upper] = pickle.load( open( filename, "rb" ) )        
        print(f'success')
    except:
        print(f'error  ->  quit')
        quit()

    
    
    
    
    DEE=DictLU_Extract_Exact(dicts_upper,dicts_lower)     
 
     
    mychunksize=100
    njobs = 25
    
    


    
    sqlstring = f'''select * from publ.names3_pubmed_baseline where affiliation is not null
                 ; '''
    
    dff=pd.read_sql(sqlstring,engine)
    print(f'fetched {len(dff)} datasets from DB done')
    
    ## prepare: not passing a df around -> passing a list of tuples around
    dataall=[(x,y) for x,y in zip(dff['hash'],dff['affiliation'])]
    chunks = [dataall[i:i + mychunksize] for i in range(0, len(dataall), mychunksize)]
    print(f'splitted into chunksize of {mychunksize}')

    if njobs == 1:
        print('start single core mode')
        _ = [process_upload_one_df(dataset) for dataset in chunks]
        
    else:
        print(f'start multi core mode: {njobs} cores')
        pool = mp.Pool(njobs)
        _ = pool.map(process_upload_one_df,[dataset for dataset in chunks])
        pool.close() 

def process_upload_one_df(df):
    """ do the country extraction and the upload to DB for one DataFrame
        df is NOT a dataframe, it's a list of tuples
    """
    
    identifier=[x[0] for x in df]
    
    d=[x[1] for x in df]
    
    
    resmeshid = [extraction_words(x,DEE) for x in d]
    result = [x[0] if len(x)>0 else '' for x in resmeshid]
    
    #print(extraction_words(d[0],DEE)[0])
    
    for thisidentifier,   thismeshid,affiliationtxt in zip(identifier,result,d):
        if len(result) > 0:       
            if thismeshid!='':
                sqlstring = f'''update publ.names3_pubmed_baseline set country_iso_text = '{thismeshid}' where hash = '{thisidentifier}' and affiliation = '{proc_sqlstring(affiliationtxt)}'; '''
                #print(sqlstring)
                try:                                              
                    connection = engine.connect()    
                    connection.execute(sqltxt(sqlstring))
                    _=connection.close()       
                except:
                    print('ERROR: ',sqlstring)
    
    
def proc_array_string(txt):
    """ not in use ... 
    """
    txt=[x.replace("'",' ').replace('"',' ').strip() for x in txt]
    
    return txt    


def proc_sqlstring(sqlword):
    sqlword = sqlword.replace("'","''")
    sqlword = sqlword.replace(':','\:')
    return sqlword 


def extraction_words(thistext,myDEE):
    """extract MeSH terms and IDs from given text
    """
    myDEE.fast(thistext)
    res2 = myDEE.fast_ids
    
    return res2     








if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'''
    extract country names from text 
    give back the corresponding 2 letter ISO code
    ''', formatter_class=argparse.RawTextHelpFormatter)
    

    args = parser.parse_args()
    
    main(args)
