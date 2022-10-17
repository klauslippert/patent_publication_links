## creates a dictionary which is used with keywordextraction.py
## with UNTERM english, spanish, french country-names and country-ISOs

import pandas as pd
import pickle

df0 = pd.read_csv('https://raw.githubusercontent.com/klauslippert/country-codes/master/data/country-codes.csv')


df1 = df0[['ISO3166-1-Alpha-2',
          'UNTERM Spanish Formal','UNTERM Spanish Short','official_name_es',
          'UNTERM English Formal','UNTERM English Short','official_name_en',
          'UNTERM French Formal','UNTERM French Short','official_name_fr',
          'CLDR display name',
]]

myextra = pd.DataFrame({'ISO3166-1-Alpha-2':['DE','UK','US','IT'],
              'name':['Deutschland','United Kingdom','USA','Italia']})

df2=pd.concat([
    df1[['ISO3166-1-Alpha-2','UNTERM Spanish Formal']].rename(columns={'UNTERM Spanish Formal':'name'}),
    df1[['ISO3166-1-Alpha-2','UNTERM Spanish Short']].rename(columns={'UNTERM Spanish Short':'name'}),
    df1[['ISO3166-1-Alpha-2','official_name_es']].rename(columns={'official_name_es':'name'}),
    df1[['ISO3166-1-Alpha-2','UNTERM English Formal']].rename(columns={'UNTERM English Formal':'name'}),
    df1[['ISO3166-1-Alpha-2','UNTERM English Short']].rename(columns={'UNTERM English Short':'name'}),
    df1[['ISO3166-1-Alpha-2','official_name_en']].rename(columns={'official_name_en':'name'}),
    df1[['ISO3166-1-Alpha-2','UNTERM French Formal']].rename(columns={'UNTERM French Formal':'name'}),
    df1[['ISO3166-1-Alpha-2','UNTERM French Short']].rename(columns={'UNTERM French Short':'name'}),
    df1[['ISO3166-1-Alpha-2','official_name_fr']].rename(columns={'official_name_fr':'name'}),
    df1[['ISO3166-1-Alpha-2','CLDR display name']].rename(columns={'CLDR display name':'name'}),
    myextra
],axis=0)

df3=df2.drop_duplicates(keep='first')

df4 = df3[[False if str(x)=='nan' else True for x in df3['name']]].reset_index(drop=True)

lookuplist = df4.rename(columns={'ISO3166-1-Alpha-2':'id',    'name':'term'})

## now use the keyword_extraction "library" (it's only a file)
## to make a pickle file for later use
from keyword_extraction import DictLU_Create_Dict
from keyword_extraction import DictLU_Extract_Exact
DCC = DictLU_Create_Dict(lookuplist)
dicts_lower = DCC.dicts_lower
dicts_upper = DCC.dicts_upper

with open('/home/user/data/supplement/country_name_iso_dict.p', 'wb') as handle:
    pickle.dump([dicts_lower,dicts_upper], handle)
    
    
## an example of usage:
#DEE=DictLU_Extract_Exact(dicts_upper,dicts_lower)
#text='Department of Anesthesia, Dalhousie University, IWK Health Centre, Halifax, Nova Scotia, Canada. allen.finley@dal.ca.'
#DEE.fast(text)
#print(DEE.fast_ids[0])

    
    
