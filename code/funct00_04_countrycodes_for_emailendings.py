print('create a table with ISO countrycodes and top level domains')
print('which is used to extract country from email-addresses')
print('-> publ.countrycodes')

import wget
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool



## warnings off
import warnings
warnings.filterwarnings("ignore")
## db connection
engine=create_engine('postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres')
## download data
_=wget.download('https://raw.githubusercontent.com/klauslippert/country-codes/master/data/country-codes.csv',
                out='/home/user/data/supplement')
## load data
cc=pd.read_csv('/home/user/data/supplement/country-codes.csv')
## processing
cols = ['ISO3166-1-Alpha-2',
        'ISO4217-currency_country_name',
        'UNTERM English Formal',
        'UNTERM English Short',
        'official_name_en',
        'UNTERM French Formal',
        'UNTERM French Short',
        'official_name_fr',
        'CLDR display name'
        ]
cc_short = cc[cols]
for col in cols:
    cc_short[col]=[str(x) for x in cc_short[col]]
cc_short=cc[['CLDR display name','ISO3166-1-Alpha-2','TLD']]
cc_short['TLD']=[str(x).split('.')[-1] for x in cc_short['TLD']]
cc_short.loc[ cc_short['ISO3166-1-Alpha-2']=='US',  'CLDR display name'        ] ='USA'


## upload to DB
cc_short.to_sql('countrycodes',engine,schema='publ',if_exists='replace',index=False)


