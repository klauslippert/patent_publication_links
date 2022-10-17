import requests
from datetime import datetime
import pandas as pd
from itertools import product
from string import ascii_lowercase
from random import choice
import os
import argparse
import logging
import multiprocessing as mp
from pathlib import Path




__version = "1.2"
__date = "Feb 2021"
__author = "Klaus Lippert"

def main(args):
    global url
    global startdate
    global enddate
    
    if args.dry_run:
        logger.critical('This is a DRY RUN - nothing will be changed!')
    else:
        logger.critical('This is a REAL RUN - files will be changed and downloaded!')
    
    
    ## starting page of EPO REST API
    url='https://data.epo.org/publication-server/rest/v1.2/publication-dates'
 
    ## download in which time period
    startdate = args.start # e.g. '2020-12-24'
    enddate   = args.end   # e.g. '2021-02-10'
 
    foldernames   = create_structure()
    actual_list   = get_actual_list()
    expected_list_unique = get_expected_list()
    download_list,rm_list = create_list_diff(actual_list,expected_list_unique)
    
    if args.dry_run:
        if args.remove_doubles:
            logger.warning('you cannot use flag --rm together with flag --dry')
        else:
            pass
    else: 
        if args.remove_doubles:
            _ = remove_doubles(rm_list)
        else:
            pass
    
    
    if args.list:
        _ = write_list_2_file(expected_list_unique)
        
    
    if args.dry_run:
        pass
    else:
        _ = download_data(foldernames, download_list)
        logger.info('download finished')
    
    logger.info('done')    
    

def remove_doubles(rm_list):
    
    [os.remove(x) for x in rm_list]
    logger.info(f'deleted {len(rm_list)} doubles from disc')
    return


def write_list_2_file(xml_urls):

    outfilename =  headfolder+'/'+headfolder+'_expected.csv'
    with open(outfilename, 'w') as f:
        for item in xml_urls:
            f.write(f'{item[0]},{item[1]}\n')
    logger.info(f'url + filenames -> {outfilename}')
    return
    
def create_structure():
    global headfolder
    
    ## create folderstructure for storing 
    headfolder=f'''EPOxml_{startdate.replace('-','')}-{enddate.replace('-','')}'''
    foldernames = [headfolder+'/'+x[0]+x[1] for x in product(ascii_lowercase,ascii_lowercase)]
    
    try:
        _=os.mkdir(headfolder)
        logger.info(f'created folder {headfolder}')
    except:
        logger.warning(f'{headfolder} seems to already exist.checking for / update subfolders')
        
    for thisfolder in foldernames:
        try:
            os.mkdir(thisfolder)
        except:
            pass
        
    logger.info(f'created folder structure inside {headfolder}')
    
    return foldernames
        

def get_actual_list():
    
    list_actual=[]
    for path in Path(headfolder).rglob('*.xml'):
        list_actual.append((str(path),path.name))
    
    logger.info(f'searched {headfolder} for xml files, found {len(list_actual)}')
    return list_actual
    
def get_expected_list():
    
    def list_of_weeks():
        a=requests.get(url).text.split('href="')[1:]
        b=[x.split('"')[0] for x in a]
        res = pd.DataFrame({'url':b,
                            'datum':[datetime.strptime(x.split('/')[-2],'%Y%m%d') for x in b]})
        return res
    
    def list_of_patent_urls(thisurl):
        a=requests.get(thisurl)
        b=a.text.split('href="')[1:]
        c=[x.split('"')[0] for x in b]
        d=[x+'/document.xml' for x in c]
        return d


    
    lowtotal = list_of_weeks()


    low = lowtotal[ (lowtotal['datum'] >= datetime.strptime(startdate,'%Y-%m-%d')) &
                    (lowtotal['datum'] <=  datetime.strptime(enddate,'%Y-%m-%d')) ].reset_index(drop=True)
    
    tmp=[]
    for ii in range(len(low)):
        tmp2=list_of_patent_urls(low['url'][ii])
        tmp.append(tmp2)
        logger.debug(f'{ii+1} of {len(low)}: added {len(tmp2)} urls to url-list')
    all_patent_urls = [item for sublist in tmp for item in sublist]
    ## adding filenames
    xml_urls=[(x,x.split('/')[-2]+'.xml') for x in all_patent_urls]
    
    xml_urls_unique=list(set(xml_urls))
    xml_urls_unique=[list(x) for x in xml_urls_unique]
    
    logger.info(f'found {len(xml_urls)} ({len(xml_urls_unique)} unique) xml at the EPO API for this time period')
    
    return xml_urls_unique


def download_one_xml(thisurl, foldernames):
        
        folder = choice(foldernames)
        tries=1
        while tries < 10:
            #logger.debug(f'''{thisurl[0]}  ->  {folder+'/'+thisurl[1]}''')  
            #thisurl[0]=thisurl[0].replace('http','https')
            logger.debug(f'''{thisurl[0]}  ->  {folder+'/'+thisurl[1]}''')  
            
            #_ = wget.download(thisurl[0], out=folder+'/'+thisurl[1])
            try:
                r = requests.get(thisurl[0])
                if r.status_code==200:
                    tries = 100
                    with open(folder+'/'+thisurl[1], 'w') as f:    # 'wb' !?
                        f.write(r.text)

                else:
                    if tries in [1,2]:
                        logger.warning(f'try {tries} failed with code {r.status_code}  ...{thisurl[0][-35:]}  RETRY')                    
                    else:
                        logger.error(f'try {tries} failed with code {r.status_code}  ...{thisurl[0][-35:]}  SKIP')                    
                    tries=tries+1
            except:
                logger.error(f'complete fail of GET command {thisurl[0]}  SKIP')                    


def create_list_diff(actual_list, expected_list_unique):
    
    ### check actual list for duplicates
        
    df_actual=pd.DataFrame({'name_actual':[str(x[1]) for x in actual_list],
                            'path_actual':[str(x[0]) for x in actual_list]
                           })  
    df_actual_unique = df_actual.drop_duplicates(subset='name_actual',keep='first')   

    df_remove = df_actual[df_actual.duplicated(subset='name_actual',keep='first')]
    rm_list=df_remove['path_actual'].to_list()
    
    
    logger.info(f'found {len(rm_list)} double files from disc. use flag --rm to remove the duplicates except one.')

    ### combine actual and expected files for getting download list
    df_expected_unique = pd.DataFrame({'name_expected':[str(x[1]) for x in expected_list_unique],
                                       'url':[str(x[0]) for x in expected_list_unique]
                                      })
    
    
    dfall = df_expected_unique.merge(df_actual_unique,left_on='name_expected',right_on='name_actual',how='outer')
    
    dfall['name_actual']=[str(x) for x in dfall['name_actual']]  ## to filter now on <str> == 'nan'
    
    df_download = dfall[dfall['name_actual']=='nan']
    
    
    download_list=[[x,y] for x,y in zip(df_download['url'],df_download['name_expected'])]
    
    logger.info(f'{len(download_list)} will be downloaded from EPO API')

    return download_list,rm_list
    
     
def download_data(foldernames, download_list):
    ## for development (error handling test)
    #download_list [8]=(download_list[8][0]+'xxx','test')
    if args.njobs==1:
        logger.info('download starts now in single core mode')
        _ = [download_one_xml(x,foldernames) for x in download_list]
    else:
        logger.info(f'download starts now in multi core mode: {args.njobs} cores')
        pool = mp.Pool(args.njobs)
        _ = pool.starmap(download_one_xml,[[xmlfile,foldernames] for xmlfile in download_list])
        pool.close()
        
        
        
        
        
        
        
if __name__ == '__main__':
    ## get the command line arguments
    parser = argparse.ArgumentParser(description=f'''
    ############################################
    download patent data as xml from EPO site
    https://data.epo.org/publication-server/rest/v1.2/publication-dates
    ############################################

    by {__author} at ZBMED
    in {__date}
    version = {__version}
    ''', formatter_class=argparse.RawTextHelpFormatter)

    required = parser.add_argument_group('required arguments')
    required.add_argument("-s", "--start",
                        dest='start',
                        required=True,
                        help="start date in format YYYY-MM-DD e.g. 2020-12-24")
    required.add_argument("-e", "--end",
                        dest='end',
                        required=True,
                        help="end date in format YYYY-MM-DD e.g. 2021-02-10")
    parser.add_argument("-d", "--debuglevel",
                        choices=['critical','error','warning','info','debug'],  
                        dest='debuglevel',
                        default='info',  
                        help="logging level as in library 'logging'. default = 'info'")    
    parser.add_argument("-n", "--njobs",
                        dest='njobs',
                        default=1,  
                        type=int,
                        help="number of parallel downloads. default = 1")
    parser.add_argument("--list",
                        dest='list', 
                        action="store_true",
                        help="write urls + filenames to file")    
    parser.add_argument("--dry",
                        dest='dry_run',
                        action="store_true",
                        help="doing a dry run: everything but no download")
    parser.add_argument("--rm",
                        dest='remove_doubles',
                        action="store_true",
                        help="removing double xml files from disc")


    
    args = parser.parse_args()
    
    ## logging
    logger=logging.getLogger()
    logger.setLevel(args.debuglevel.upper())
    ch=logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s') )
    logger.addHandler(ch)
    
    
    
    ## start
    main(args)



