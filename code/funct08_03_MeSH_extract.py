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
engine=create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres',
                     poolclass=NullPool )
print(engine,'connection test:',pd.read_sql('select 1 as aa',engine)['aa'][0] )  


def main(args):
    

    global DEE 
    dicts_lower,dicts_upper, filter_lang = get_MeSH_dict(args)
    DEE=DictLU_Extract_Exact(dicts_upper,dicts_lower)     
 
     
    mychunksize=100
    njobs = 30
    
    print(f'''PY: funct08_03_MeSH_extract.py - extracting MeSH-IDs from patent text, language {filter_lang}''')

    sqlstring = f'''select 
                        patent_family, raw  
		    from publ.text_patente 
		    where lang='{filter_lang}' 
		    and patent_family not in (select patent_family from publ.text_patente_proc)
                    ;'''
    dff=pd.read_sql(sqlstring,engine)
    print(f'fetched {len(dff)} datasets from DB done')
    
    ## prepare: not passing a df around -> passing a list of tuples around
    dataall=[(x,y) for x,y in zip(dff['patent_family'],dff['raw'])]
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
    """ do the MeSH extraction and the upload to DB for one DataFrame
        df is NOT a dataframe, it's a list of tuples
    """
    
    identifier=[x[0] for x in df]#df[args.docid]
    
    d=[x[1] for x in df]
    
    
    resmeshid = [extraction_words(x,DEE) for x in d]
    
    result_df=pd.DataFrame({'patent_family':identifier,
                            'meshid':resmeshid})
    result_df.to_sql('text_patente_proc',engine, schema='publ',if_exists='append',index=False)
    
    ## that is the old version where the table is updated.
    #for thisidentifier,   thismeshid in zip(identifier,resmeshid):
    #    if len(resmeshid) > 0:       
    #    
    #        sqlstring = f'''update quamedfo.text_patente set meshid = '{proc_array_string(thismeshid)}' 
	                    #where hash_patfam = '{thisidentifier}'; '''
#            try:                                              
#                connection = engine.connect()
                
#                connection.execute(sqltxt(sqlstring))
#                _=connection.close()       
#            except:
#                print('ERROR: ',sqlstring)
    
    
def proc_array_string(txt):
    """processing of list of MeSH-IDs
    to fit into a SQL update statement done with sqlalchemy
    """
    txt=[x.replace("'",' ').replace('"',' ').strip() for x in txt]
    txt='{"'+'","'.join(txt)+'"}'
    return txt    


def extraction_words(thistext,myDEE):
    """extract MeSH terms and IDs from given text
    """
    myDEE.fast(thistext)
    res2 = myDEE.fast_ids
    
    return res2     


def get_MeSH_dict(args):
    ## load MeSH dictionary
    if args.lang == 'en':
        mesh_filename = 'MeSH_dict_english.p'
        filter_lang='en'
    if args.lang == 'de':
        mesh_filename = 'MeSH_dict_german.p'
        filter_lang='de'
    if args.lang == 'fr':    
        mesh_filename = 'MeSH_dict_french.p'
        filter_lang='fr'
    
    print(f'loading MeSH data from {mesh_filename}')
    try:
        [dicts_lower,dicts_upper] = pickle.load( open( mesh_filename, "rb" ) )        
        print(f'success')
    except:
        print(f'error  ->  quit')
        quit()

    return dicts_lower,dicts_upper, filter_lang






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'''
    extract MeSH terms IDs from text 
    in english, german and french, 
    give back the corresponding mainheadings
    ''', formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("--lang",
                        dest='lang',
                        choices=['en','de','fr'],
                        required=True,
                        help="which language")  
    
    args = parser.parse_args()
    
    main(args)
