import pandas as pd
import re

class DictLU_Create_Dict():
    def __init__(self,df):
        '''
        USAGE: 
            from dictionary_lookup import *
            DC = DictLU_Create_Dict(df_lookuplist)
            dicts_lower = DC.dicts_lower
            dicts_upper = DC.dicts_upper
            
        input: df with columns "id" and "term"
        output: 2 lists of dicts (for uppercase and lowercase words)
                sorted each by num of grams
                with each having:
                    key: ' ' + term + ' '  
                    value: MeSH-id
        
        2do check input type
        2do check input column-names
        2do bug: if one of the dicts_* is empty -> error
        '''
        self.df = df
        _=self.split_into_upper_lower()
        
        self.dicts_upper = self.create_dicts(self.dfupper,False)
        self.dicts_lower = self.create_dicts(self.dflower,True)
        
        
    def split_into_upper_lower(self):
        ''' split into plain upper and upper/lower-mixed words
            keep upper ones and lower/mixed ones
        '''
        self.df['pure_upper']=[x.isupper() for x in self.df['term']]
        self.df['numb_grams'] = [len(s.split()) for s in self.df['term']]

        self.dfupper = self.df[self.df['pure_upper']==True]\
                       .reset_index(drop=True)\
                       .drop(columns='pure_upper')
        self.dflower = self.df[self.df['pure_upper']==False]\
                       .reset_index(drop=True)\
                       .drop(columns='pure_upper')
    
    def create_dicts(self,df2,flag_lower):
        ''' create list of dicts with one dict for each n-gram.
            key: term  value: id
        '''
        alldicts=[]
        
        for ngrams in range(1,max(df2['numb_grams'])+1):
            df3 = df2[df2['numb_grams']==ngrams].reset_index(drop=True)
            if flag_lower:
                alldicts.append(dict(zip([x.lower() for x in df3['term']],
                                         df3['id'])))
            else:
                alldicts.append(dict(zip(df3['term'],
                                         df3['id'])))
        return alldicts        
    
    
class DictLU_Extract_Exact():
    def __init__(self,dicts_upper,dicts_lower):
        
        '''USAGE:
           from dictionary_lookup import *
           DEE=DictLU_Extract_Exact(dicts_upper,dicts_lower)
           DEE.run(text)
           result = DE.result
           
        '''
        #load list of dicts
        self.dicts_upper = dicts_upper
        self.dicts_lower = dicts_lower

        self.punct_list = [' ',',', '.', '?', '!','"',':','’',
                           '(',')','[',']','{','}' ]        
        self.punct_list_small = [',', '\.', '\?', '!','"',':','’',
                           '\(','\)','\[','\]','{','}' ]  
        
    def fast(self,raw_text):
        '''fast extraction process:
           take only the first occurence of a term,
           no index information, etc.
        '''
        self.text = raw_text
        #preprocess 
        text = ' '+raw_text+' '
        for punct in self.punct_list_small:
            text=re.sub(punct,' ',text)    
           
        #print('|'+text+'|')    
        def extract_fast(all_dicts,text):
            found_ids=[]
            found_words=[]
            for this_dict in all_dicts[::-1]:
                
                for searchword in list(this_dict.keys()):
                    idx=text.find(' '+searchword+' ')
                    
                    if idx!=-1:
                        
                        found_ids.append(this_dict[searchword])
                        found_words.append(searchword)
                        #print('|'+text[idx:idx+len(searchword)+2]+'|',searchword,idx)
                        text = re.sub(searchword,'_',text)
                        
                        
            return text,found_ids, found_words
        
        text, self.found_ids_upper,self.found_words_upper = extract_fast(self.dicts_upper,text)
        
        text=text.lower()
        
        text, self.found_ids_lower,self.found_words_lower = extract_fast(self.dicts_lower,text)
        
        self.fast_ids = self.found_ids_upper + self.found_ids_lower
        
        
    def full(self,raw_text):
        '''full extraction process
        '''
        _=self.fast(raw_text)
        
        
        
        def extract_full(searchwords,meshids,text):
            found_words=[]
            for searchword,meshid in zip(searchwords,meshids):   
                #print(searchword,meshid)
                
                while 1==1:
                    #print(searchword)
                    searchword2=' '+searchword+' '
                    idx = text.find(searchword2)
                    if idx == -1:
                        break
                    
                    start_index = idx 
                    end_index = start_index + len(searchword2)
                    
                    
                    found_words.append((searchword,meshid,start_index,end_index-2))
                    ## anyway, mask the word for next loop
                    text = text[:start_index] +\
                               ' '+'_'*(len(searchword2)-2)+' ' +\
                               text[end_index:]
                    #print(text)
                    #print('****')
            return text,found_words                           
                        
                        
        #preprocess 
        text = ' '+raw_text+' '
        for punct in self.punct_list_small:
            text=re.sub(punct,' ',text)    
        #print(text)
        
        if len(self.found_words_upper) > 0:
            text,res_words_upper=extract_full(self.found_words_lower,self.found_ids_lower,text)
        else:
            res_words_upper=[]
        
        text=text.lower()
        text,res_words_lower=extract_full(self.found_words_lower,self.found_ids_lower,text)
        found_words=res_words_upper+res_words_lower
        
        #self.ff=found_words
        #self.text = raw_text
        #for punct in self.punct_list_small:
        #    raw_text=re.sub(punct,' ',raw_text)  
        
        #text, found_words_upper = self.extract(self.dicts_upper,raw_text)
        
        #text = text.lower()
        #text, found_words_lower = self.extract(self.dicts_lower,text)                    
        #print(found_words_lower)
        
        #found_words = found_words_upper + found_words_lower
                    
        unique_ids = list(set([x[1] for x in found_words]))

        words = [x[0] for x in found_words]
        ids   = [x[1] for x in found_words]
        start = [x[2] for x in found_words]
        end   = [x[3] for x in found_words]

        idx=[]
        for this_id in unique_ids:
            idx.append([i for i,val in enumerate(ids) if val==this_id])
    
        result=dict()   
        for this_idx in idx:
            result.update( {ids[this_idx[0]]: {'count':len(this_idx),
                                               'term': words[this_idx[0]] ,  
                                               'pos':[(start[x],  end[x]) for x in this_idx]
                                              }
                            }
                          )
        self.result=result
        #self.proc_text = text
        
    def extract(self,all_dicts,text):   
        bkp=text 
        found_words=[]
        text=' '+text+' '
        for this_dict in all_dicts[::-1]:
    
            for searchword in list(this_dict.keys()):
            #searchword = proc_punct(searchword)
                
        
                while 1==1:
                    searchword2=' '+searchword+' '
                    start_index = text.find(searchword2)
                    
                    if start_index not in [-1]:
                        end_index = start_index + len(searchword2)
                        ## is it a word with only punctuation as sourounding?
                        ## yes ? then extract it
                        
                        
                        #if ( (start_index == 0) and \
                        #     (text[end_index] in self.punct_list) ) \
                        #   or \
                        #   ( (text[start_index-1] in self.punct_list) and \
                        #     (text[end_index] in self.punct_list) ) :
                           
                        search_id=this_dict[searchword]
                        

                        found_words.append((searchword,search_id,start_index,end_index))
                        #else:
                        #    print('nonono')
                            
                            #start_index=start_index-1
                        #end_index=end_index-2
                        print('|'+text[start_index:end_index]+'|','|'+text[start_index-1:end_index+1]+'|',search_id)
                        
                        ## anyway, mask the word for next loop
                        text = text[:start_index] +\
                               '_'*len(searchword2) +\
                               text[end_index:]
                           
                        
                    
                        
                           
                    else: 
                        break
        return text, found_words
    
            
    def create_html(self):
        '''creates an html page out of the text 
           with the extracted words in red
        '''
        text=self.text
        a=[x[1]['pos'] for x in self.result.items()]
        b=[item for sublist in a for item in sublist]
        c = sorted(b, key=lambda tup: tup[0])
        
        pre = '<!DOCTYPE html> <html>  <head>  <!-- head definitions go here -->    </head>    <body>'
        post = '</body> </html>'

        string=pre+text[:c[0][0]]
        for i in range(0,len(c)):
            string = string + '<font color="red">{'+text[c[i][0]:c[i][1]]+'}</font>'
            if i != len(c)-1:
                string = string + text[c[i][1]:c[i+1][0]]
            
        string = string + text[c[-1][1]:]+post
        
        self.html=string

        # try: as hover information give the mesh-ID
        #d=[x[0] for x in DEE.result.items()]
        #print(d)
        #<span title="I am hovering over the text">This is the text I want to have a mousover</span>

        
        
        

    
class DictLU_Extract_Fuzzy():
    def __init__(self,dicts_upper,dicts_lower):
        ''' the idea is to calc a string distance (levenshtein or jaccard) score to 
        find mesh terms with typos, singular/plural, etc.
        '''
        pass
    
