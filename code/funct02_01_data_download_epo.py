import requests
from datetime import datetime
import pandas as pd
from itertools import product
from string import ascii_lowercase
from random import choice
import os
#import argparse

import multiprocessing as mp
from pathlib import Path
import time

## starting page of EPO REST API
global url
url='https://data.epo.org/publication-server/rest/v1.2/publication-dates'

## download in which time period
startdate = '2000-01-01'
enddate   = '2015-01-01'


def main():
    # environment variables
    env = os.environ
    njobs=int(env['njobs_epo_download'])
    if njobs==1:
        print('download in single core mode')
    else:
        print(f'download in multi core mode: {njobs} cores')

    foldernames   = create_structure()
    actual_list   = get_actual_list()
    expected_list_unique = get_expected_list()

    print('some example urls:',[x[0] for x in expected_list_unique[:3]])

    download_list,rm_list = create_list_diff(actual_list,expected_list_unique)
    print(len(download_list))
#    exit()

    if njobs==1:
        _ = [download_one_xml(x,foldernames) for x in download_list]
    else:
        pool = mp.Pool(njobs)
        _ = pool.starmap(download_one_xml,[[xmlfile,foldernames] for xmlfile in download_list])
        pool.close()

def create_structure():
    global headfolder
    ## create folderstructure for storing
    headfolder='/home/user/data/patent'
    foldernames = [headfolder+'/'+x[0]+x[1] for x in product(ascii_lowercase,ascii_lowercase)]
    try:
        _=os.mkdir(headfolder)
        print(f'created folder {headfolder}')
    except:
        print(f'{headfolder} seems to already exist. checking for / update subfolders')
    for thisfolder in foldernames:
        try:
            os.mkdir(thisfolder)
        except:
            pass
    print(f'created folder structure inside {headfolder}')
    return foldernames

def get_actual_list():
    
    list_actual=[]
    for path in Path(headfolder).rglob('*.xml'):
        list_actual.append((str(path),path.name))
    
    print(f'searched {headfolder} for xml files, found {len(list_actual)}')
    return list_actual


def get_expected_list():
    
    def list_of_weeks():
        #print(url)
        a=requests.get(url).text.split('href="')[1:]
        #print(a)
        
        b=[x.split('"')[0] for x in a]
        res = pd.DataFrame({'url':['http://data.epo.org'+x for x in b],
                            'datum':[datetime.strptime(x.split('/')[-2],'%Y%m%d') for x in b]})
        return res
    
    def list_of_patent_urls(thisurl):
        a=requests.get(thisurl)
        b=a.text.split('href="')[1:]
        c=[x.split('"')[0] for x in b]
        d=['http://data.epo.org'+x+'/document.xml' for x in c]
        return d


    
    lowtotal = list_of_weeks()
    #print(lowtotal.head())

    low = lowtotal[ (lowtotal['datum'] >= datetime.strptime(startdate,'%Y-%m-%d')) &
                    (lowtotal['datum'] <=  datetime.strptime(enddate,'%Y-%m-%d')) ].reset_index(drop=True)
    
    tmp=[]
    for ii in range(len(low)):
        tmp2=list_of_patent_urls(low['url'][ii])
        tmp.append(tmp2)
        print(f'{ii+1} of {len(low)} weeks: added {len(tmp2)} urls to url-list')
    all_patent_urls = [item for sublist in tmp for item in sublist]
    ## adding filenames
    xml_urls=[(x,x.split('/')[-2]+'.xml') for x in all_patent_urls]
    
    xml_urls_unique=list(set(xml_urls))
    xml_urls_unique=[list(x) for x in xml_urls_unique]
    
    print(f'found {len(xml_urls)} ({len(xml_urls_unique)} unique) xml at the EPO API for this time period')
    
    return xml_urls_unique


def create_list_diff(actual_list, expected_list_unique):
    
    ### check actual list for duplicates
        
    df_actual=pd.DataFrame({'name_actual':[str(x[1]) for x in actual_list],
                            'path_actual':[str(x[0]) for x in actual_list]
                           })  
    df_actual_unique = df_actual.drop_duplicates(subset='name_actual',keep='first')   

    df_remove = df_actual[df_actual.duplicated(subset='name_actual',keep='first')]
    rm_list=df_remove['path_actual'].to_list()
    
    
    print(f'found {len(rm_list)} double files from disc. use flag --rm to remove the duplicates except one.')

    ### combine actual and expected files for getting download list
    df_expected_unique = pd.DataFrame({'name_expected':[str(x[1]) for x in expected_list_unique],
                                       'url':[str(x[0]) for x in expected_list_unique]
                                      })
    
    
    dfall = df_expected_unique.merge(df_actual_unique,left_on='name_expected',right_on='name_actual',how='outer')
    
    dfall['name_actual']=[str(x) for x in dfall['name_actual']]  ## to filter now on <str> == 'nan'
    
    df_download = dfall[dfall['name_actual']=='nan']
    
    
    download_list=[[x,y] for x,y in zip(df_download['url'],df_download['name_expected'])]
    
    print(f'{len(download_list)} xml-files will be downloaded from EPO API')

    return download_list,rm_list


def download_one_xml(thisurl, foldernames):
        
        folder = choice(foldernames)
        tries=1
        while tries < 6:
            #logger.debug(f'''{thisurl[0]}  ->  {folder+'/'+thisurl[1]}''')  
            #thisurl[0]=thisurl[0].replace('http','https')
            print(f'''...{thisurl[0][-35:]}  ->  {folder+'/'+thisurl[1]}''')  
            
            #_ = wget.download(thisurl[0], out=folder+'/'+thisurl[1])
            try:
                r = requests.get(thisurl[0])
                sc = r.status_code
                        
                if sc == 200:
                    if "The fair-use policy" in r.text:
                        print('THIS IS A MESSAGE FROM THE EPO:')
                        print('The fair-use policy limits a given IP address to 5 GB of download in any sliding window of 7 days.')
                        print('stopping now, re-run this script again in 24h again -> bye, exit')
                        exit()

		        
                    with open(folder+'/'+thisurl[1], 'w') as f:    # 'wb' !?
                        f.write(r.text)
                    #print(sc,'example text',r.text[:70])
                    tries = 100
                else:
                    print(sc,'that was try',tries,'did not work')
                    tries=tries+1
            except:
                pass
                #print(f'complete fail of GET command ...{thisurl[0][-35:]}  SKIP')                    



main()
