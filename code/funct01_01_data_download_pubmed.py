from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy.pool import NullPool
from datetime import datetime as dt
import pandas as pd
import hashlib
import gzip
import glob
import json
#import time

#### !!!
import my_pubmed_parser as pp

import pandas as pd
import os
from ftplib import FTP

## connection to postgres . this should be moved to a utils.py file
cred={'PGUSER':'postgres',
      'PGPASSWORD':'postgres',
      'PGHOST':'127.0.0.1',
      'PGDATABASE':'postgres',
      'PGPORT':5432
}
#+psycopg2
engine=create_engine('postgresql://{}:{}@{}:{}/{}'.format(cred['PGUSER'],
                     cred['PGPASSWORD'],cred['PGHOST'],cred['PGPORT'],cred['PGDATABASE']),
                    poolclass=NullPool
                )
print(engine)

try:
    _=pd.read_sql('select 1;',engine)
    print('connection test',_)
except:
    print('error connecting to DB -> exit now')
    exit()

def list_of_ftp_files():
    ## create list of files on pubmed ftp server
    url='ftp.ncbi.nlm.nih.gov'
    ftp = FTP(url)
    ftp.login()
    ftp.cwd('pubmed/baseline')
    filesftp = [x for x in ftp.nlst() if x.find('md5') == -1]
    ftp.quit()
    filesftp=[x for x in filesftp if x != 'README.txt']
    print(f'found {len(filesftp)} files on pubmed ftp server. here are the first 2: {filesftp[:2]}' )
    return filesftp

def list_of_local_files():
    ## create list of files alread on local filesystem
    pathname = '/home/user/data/publication/'
    fileslocal = [x.split('/')[-1]+'.gz' for x in glob.glob(pathname+'*xml')]
    print(f'found {len(fileslocal)} files locally in {pathname}')   
    return fileslocal


def download_list(filesftp,fileslocal):
    ## create downloadlist as diff files local / files on ftp
    downloadlist=[x for x in filesftp if x not in fileslocal]
    ##debugging
#    downloadlist=downloadlist[:5]
#    downloadlist=['pubmed22n0458.xml.gz']
    ##
    print(f'   -> {len(downloadlist)} files will be downloaded from the ftp server and uploaded to local postgresql')   
    return downloadlist






def download_complete_download_list(downloadlist):
    pathname='/home/user/data/publication/'
    url='ftp.ncbi.nlm.nih.gov'
    
    for ii,filename in enumerate(downloadlist):
        ftp = FTP(url)
        _=ftp.login()
        ftp.cwd('pubmed/baseline') 
        cont=False
        try:
            print(f'download + unpack {filename} as {ii+1} of {len(downloadlist)} files')
            ftp.retrbinary("RETR " + filename ,open(pathname+filename, 'wb').write)
            cont=True
        except:
            print(f'        error downloading -> skipping')
            cont=False
        if cont:
            try:
                os.system(f'''gzip -d {pathname+filename}''')    
            except:
                print(f'        error extracting')
#        if ii!=0 and ii%25 == 0:   #wait every 25th file for some time 
#            print('waiting...')
#            time.sleep(69)	    
	    
        ftp.quit()
    #print(_)

    return None


## download files from ftp and unpack them
filesftp     = list_of_ftp_files()

for ii in [1,2,3]:
    print(f'##################')
    print(f'attempt {ii} of 3:')
    
    fileslocal   = list_of_local_files()
    downloadlist = download_list(filesftp,fileslocal)
    _=download_complete_download_list(downloadlist)
    print(f'{len(fileslocal)} {len(downloadlist)}')

print('hopefully all files are now successfully downloaded, check manually and change code if needed')


## upload files to postgresql into schema "pubmed_baseline" table "stage"

filelist = glob.glob('/home/user/data/publication/*.xml')

errorlist=[]

for ii,filename in enumerate(filelist):
    
    print(f'processing {ii+1} of {len(filelist)}: {filename}')
    try:
        data= pp.parse_medline_xml(filename,
                         year_info_only=False,
                         nlm_category=False,
                         author_list=True,
                         reference_list=True)

        data2 = [json.loads(json.dumps(x)) for x in data]
 
        df = pd.DataFrame({'loaddate':None,
                       'data':[x for x in data2] ,
                       'hash':None})
        df.loaddate=dt.now()
        df.hash=[hashlib.sha1(str(x).encode('utf-8')).hexdigest() for x in df.data]
 
        print('    upload to DB')
        df.to_sql('stage',
                  engine,
                  schema='pubmed_baseline',
                  if_exists='append',
                  index=False,
                  dtype={'data': types.JSON}
                 )
    except:
        errorlist.append((ii,filename))
        print('    ERROR -> error_list')

print('ERRORs in:')
print(errorlist)
