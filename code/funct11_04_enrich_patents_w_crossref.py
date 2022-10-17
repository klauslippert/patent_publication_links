import pandas as pd
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy import text as sqltxt
import os
from collections import Counter
import re
import requests
from nltk.stem import PorterStemmer
import multiprocessing as mp
import argparse
import requests_cache


env=os.environ
engine=create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres',
                     poolclass=NullPool )
print(engine,'connection test:',pd.read_sql('select 1 as aa',engine)['aa'][0] )  

global porter
porter = PorterStemmer()

requests_cache.install_cache('crossref_cache')

def main(args):
    global myemail 
    myemail = args.myemail
    
    mychunksize = 100
    njobs = 5  #max 5 !
    
    dff = pd.read_sql('''select distinct 
                            author,
                            article_title,
                            serial_pubyear,
                            serial_title_full,
                            querystring 
                        from publ.ref_raw_patents 
                        where trim(querystring)!='' 
                        and crossref_doi is null
                        ;''',engine,chunksize=mychunksize)    
    #limit 50
    
    ## only for user info
    def print_cnt(engine):
        cnt = pd.read_sql('''select count(*) from (select distinct 
                            author,
                            article_title,
                            serial_pubyear,
                            serial_title_full,
                            querystring 
                        from publ.ref_raw_patents 
                        where trim(querystring)!='' 
                        and crossref_doi is null) a 
                        ;''', engine)['count'][0]
    
        print(f'loaded {cnt} distinct datasets')
#
#   TODO:  that can be done more nicely, not repeating the complete sql statement..
#   
    _=print_cnt(engine)
    
    
    if njobs == 1:
        print('start single core mode')
        _ = [work_one_df(chunk) for chunk in dff]
    else:
        print(f'start multi core mode: {njobs} cores')
        pool = mp.Pool(njobs)
        _ = pool.map(work_one_df,[chunk for chunk in dff])
        pool.close()
    
    
def proc_sqlstring(sqlword):
    sqlword = sqlword.replace("'","''")
    sqlword = sqlword.replace(':','\:')
    return sqlword    
    
    
def work_one_df(df):
    for ii in range(len(df)):
    
        ctrl_continue, res = gather_doi(df.iloc[ii],myemail)

        # stop requesting crossref when received something different than a 200 response code
        if ctrl_continue == False:
            print(f'stopping this batch run at line {ii} of df size {len(df)} because of != 200 response code')
            break

        if res['DOI']!='':
            #print(ii,res['querystring'],res['DOI'])
            querystring = proc_sqlstring(res['querystring'])
            sqlstring = f'''update publ.ref_raw_patents set crossref_doi = '{res['DOI']}' where querystring = '{querystring}';'''
            #print(sqlstring)
            connection = engine.connect()
            connection.execute(sqltxt(sqlstring))
            _=connection.close()
        else:
            pass    
        
        
def proc_hits(hit):
    """ processing the hits from crossref, using only 6 fields"""
    mykeys  =  ['DOI','title','author','published','short-container-title','container-title']    
    result = {k:hit[k] if k in hit else '' for k in mykeys }   
    if isinstance(result['author'],list):
        authorlist=[]
        for hh in result['author']:
            if 'family' in hh.keys():
                authorlist.append(hh['family'].lower())    
            elif 'name' in hh.keys():
                authorlist.append(hh['name'].lower())    
            else:
                pass
        result['authorlist']=' '+' '.join(authorlist)+' ' 
 
    else:
        result['authorlist']=' '+str(result['author'])+' '
        
        
    if isinstance(result['title'],list):
        result['title'] = result['title'][0]    
    try:
        result['pubyear']=str(result['published']['date-parts'][0][0])
    except:
        result['pubyear']=str(result['published'])
    if isinstance(result['container-title'],list):
        result['container-title'] = result['container-title'][0].lower()
    else:
        result['container-title'] = result['container-title'].lower()
    if isinstance(result['short-container-title'],list):
        result['short-container-title'] = result['short-container-title'][0].lower()
    else:
        result['short-container-title'] = result['short-container-title'].lower()    
    result.pop('author')
    result.pop('published')
    return result

def check_hit(hit,item):
    """ compare all hits from crossref against the ref-data from a patent
        
    """
    # equal = [article_title,journal_title,pubyear,author]
    equal=[False,False,False,False]
    ## compare stemmed titles
    if ''.join(porter.stem(str(hit['title'])).split()) == ''.join(porter.stem(str(item.article_title)).split()):
        equal[0]=True
    ## compare journal names
    if (str(hit['container-title']).lower() == str(item.serial_title_full).lower()) or \
       (str(hit['short-container-title']).lower() == str(item.serial_title_full).lower()):
        equal[1]=True
    ## compare publyear
    if str(hit['pubyear']) == item.serial_pubyear :
        equal[2]=True
    ## compare authors: only one author must be equal to fullfill this requirement
    equalauthors=False
    for thisauthor in [' '+x.lower()+' ' for x in re.sub('\.',' ',re.sub(',',' ',item.author)).split()]:
        if thisauthor in hit['authorlist']:
            equalauthors=True
    if equalauthors:
        equal[3]=True
    
    # at least the pubyear must be correct:
    #if equal[2]:
    return Counter(equal)[True] 
    #else:
    #    return 0

    

def query_crossref(mystring,myemail):
    """ query crossref for 3 results"""
    mystring = re.sub('&',' ',mystring)
    
    ### new version
    querystring = f'''http://api.crossref.org/works?query.bibliographic="{mystring}"&rows=3&mailto={myemail}'''
    ## only for testing what happens if status_code != 200
    #querystring = f'''http://api.crossref.org/abkh?query.bibliographic="{mystring}"&rows=3'''
    #print(querystring)
    try:
        r=requests.get(querystring)
        #print(r.status_code)
        if r.status_code == 200:
            ctrl_continue = True
            status = r.status_code
        else:
            ctrl_continue = False
            status = r.status_code

    except:
        print(f'''error using request on crossref with: {mystring}''')
        ctrl_continue = False
        status = -1
	
    if ctrl_continue:
        #print(r.status_code,r.content)
        jj = r.json()
        allhits=jj['message']['items']
        return ctrl_continue,allhits
    else:
        print(f'''error status code {status} from crossref with: {mystring}''')
        # return nothing, exit the script
        print('#########################')
        print('in order to avoid blocking from crossref-side because of hammering the api')
        print('although they gave an error response, script will exit now.')
        print('check status codes and re-run manually')
        print('EXIT -> bye.')
        exit
	
	#return ctrl_continue,None

    
    
    ### old version:
    #my_extra_header = {'contact': myemail}   
    #querystring = f'''http://api.crossref.org/works?query.bibliographic="{mystring}"&rows=3'''
    #try:
    #    r=requests.get(querystring, headers=my_extra_header) 
    #    #print(r.status_code,r.content)
    #    jj = r.json()
    #    allhits=jj['message']['items']
    #    return allhits
    #except:
    #    print(f'''error querying crossref with: {mystring}''')
    #    return None


def gather_doi(item,myemail):
    """ complete crossref querying process"""
    # query
    ctrl_continue, allhits = query_crossref(item.querystring,myemail)
    # process hits
    #creating an empty dict.. TODO can be done more pythonic
    winnerhit={k:'' for k in ['DOI','title','authorlist','pubyear','short-container-title','container-title','querystring']}  
    if allhits:
        res_proc_hits =  [proc_hits(x) for x in allhits]
        # check hits for 4 requirements
        allchecks = [check_hit(x, item) for x in res_proc_hits]
        # choose the winner hit
        maxtrue = max(allchecks)
        winneridx=-1
        if maxtrue > 0:
            winneridx = allchecks.index(max(allchecks))
            winnerhit = res_proc_hits[winneridx]
        else:
            pass
    
    
    
        # make the result great again
        winnerhit['crossref_title'] = winnerhit.pop('title')
        winnerhit['crossref_authors'] = winnerhit.pop('authorlist')
        winnerhit['crossref_pubyear'] = winnerhit.pop('pubyear')
        winnerhit['crossref_journal_short'] = winnerhit.pop('short-container-title')
        winnerhit['crossref_journal'] = winnerhit.pop('container-title')
    
    
        winnerhit['patentref_title']=item.article_title
        winnerhit['patentref_journal_norm']=item.serial_title_full
        winnerhit['patentref_pubdate'] = item.serial_pubyear
        winnerhit['patentref_authors'] = item.author
        winnerhit['querystring']=item.querystring
        
    
    
    else:
        pass
    
    return ctrl_continue, winnerhit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'''
    enrich patente references using crossref api-calls''', formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("--email",
                        dest='myemail',
                        required=True,
                        help="provide your email to be polite to the crossref api")  
    
    args = parser.parse_args()
    
    main(args)
