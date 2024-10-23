#格式化输出
import os
import re
import sys
import csv
import json
import time
import glob
import getopt
import argparse
import pandas as pd
from tqdm import tqdm, trange


def json_to_list(Nsem,json_content: dict) -> list:
    '''解析metamap json格式,获取实体标注'''
    sent_result=[]
    anno_result=[]
    pmid_list=[]
    for document in json_content['AllDocuments']:
        for item in document['Document']['Utterances']:
            ###遍历句子
            if item['PMID'] not in pmid_list:
                pmid_list.append(item['PMID'])
            sentence=item['UttText']
            sen_id=item['PMID']+'_'+item['UttSection']+item['UttNum']
            sent_result.append([item['PMID'],sen_id,sentence])
            utt_start=int(item['UttStartPos'])
            for phrase_item in item['Phrases']:
                #metamap将句子切分为不同的片段，遍历片段
                phrasetext=phrase_item['PhraseText']
                if len(phrasetext)==1:
                    #过滤掉只有一个字符的片段
                    continue
                #phrase_start=int(phrase_item['PhraseStartPos'])-utt_start
                #phrase_end=int(phrase_item['PhraseLength'])+start
                max_score=0
                match_infor=[]
                min_matchmaplen=10
                for mapping_item in phrase_item['Mappings']:
                    #片段有多个metamap匹配结果，遍历结果，选择最佳的一个
                    mappingscore=int(mapping_item['MappingScore'][1:])
                    if max_score>mappingscore:
                        #若当前匹配分数为最高，直接选取当前匹配为最终
                        #一般最高分数最先被遍历到
                        break
                    else:
                        max_score=mappingscore
                    max_c_score=0
                    match_infor_temp=[]
                    for mc in mapping_item['MappingCandidates']:
                        #片段可能又被切分，有多个匹配，遍历
                        cui=mc['CandidateCUI']
                        match=mc['CandidateMatched']
                        normalization=mc['CandidatePreferred']
                        semtype=mc['SemTypes']
                        c_score=int(mc['CandidateScore'][1:])
                        mc_matchwords=[]#匹配原文短语
                        mc_pis=[]#位置信息
                        for pi in mc['ConceptPIs']:#匹配原文短语位置信息
                            start=int(pi['StartPos'])
                            end=int(pi['Length'])+start
                            start=start-utt_start
                            end=end-utt_start
                            mc_matchwords.append(sentence[start:end])#原文单词信息
                            mc_pis.append(str(start)+':'+str(end))#位置信息
                        mc_pis=';'.join(mc_pis)
                        mc_matchwords=';'.join(mc_matchwords)
                        if len(mc_matchwords)==1:
                            continue
                        '''
                        if ';' not in mc_pis:
                            mc_matchmaps_dis='0'
                            mp_dis_sum=0
                        else:
                            mc_matchmaps_dis=[]#匹配单词间间隔
                            mp_dis_sum=0
                            matchmaps=[]
                            for mp in mc['MatchMaps']:
                                textmatchend=int(mp['TextMatchEnd'])
                                textmatchstart=int(mp['TextMatchStart'])
                                matchmaps.append([textmatchstart,textmatchend])
                            matchmaps=sorted(matchmaps,key=lambda x:x[0])
                            textmatchend=matchmaps[0][1]
                            for mp in matchmaps[1:]:
                                mp_dis=mp[0]-textmatchend-1
                                mp_dis_sum+=mp_dis
                                mc_matchmaps_dis.append(str(mp_dis))
                                textmatchend=mp[1]
                            mc_matchmaps_dis=';'.join(mc_matchmaps_dis)
                            '''
                        match_infor_temp.append([mc_pis,mc_matchwords,cui,match,normalization,semtype,phrasetext])
                    matchmap_len=len(match_infor_temp)
                    if matchmap_len<min_matchmaplen:
                        #分数相同时，选择一个匹配片段最连贯的，而不是有间隔的
                        match_infor=match_infor_temp
                        min_matchmaplen=matchmap_len
                if match_infor!=[]:
                    for mi in match_infor:
                        #筛选需要的语义类型
                        semtmp=[]
                        for sem in mi[5]:
                            if sem in Nsem:
                                semtmp.append(sem)
                        if semtmp!=[]:
                            line=[item['PMID']]+mi[:5]+[';'.join(semtmp),sen_id,mi[-1]]
                            anno_result.append(line) 
                        
                        #mi[7]=';'.join(mi[7])
                        #line=[item['PMID']]+mi+[sen_id]
                        #anno_result.append(line)
    return(sent_result,anno_result)  
def get_filter_result(nor,metamap_word,semantic,phrase,judge,fdata,error_data):
    tag_error='n'
    tag_reserve='n'
    tag_reserve_error='n'
    tag_remove_a='n'
    custom_judge='n'
    filter_judge='n'
    filter_result=True
    for char in re.findall('\W',nor):
        nor=nor.replace(char,'_')
    if judge=='remove':
        tag_remove_a='n'
        if  nor in fdata:
            filter_judge='y'
    elif judge=='reserve':
        filter_judge='y'
        if  nor in fdata:
            filter_judge='n'
    if filter_judge=='n':
        if error_data.shape[0]!=0:
            col=error_data.loc[error_data['name']==nor]['site'].values
            judge_col=len(col)
            if judge_col >0:
                if col[0] =='c':
                    #c_list=
                    c_list=error_data.loc[error_data['name']==nor]['list'].values
                    c_str=c_list[0]
                    c_str=c_str.replace('[','')
                    c_str=c_str.replace(']','')
                    c_str=c_str.replace("'","")
                    c_str_list=c_str.split(',')
                    for str_list_single in c_str_list:
                        str_list_single=str(str_list_single.strip())
                        if metamap_word == str_list_single:
                            tag_error='y'
                elif col[0] =='d':
                    d_list=error_data.loc[error_data['name']==nor]['list'].values
                    d_str=d_list[0][2:-2]
                    '''
                    d_str=d_str.replace('[','')
                    d_str=d_str.replace(']','')
                    d_str=d_str.replace("'","")
                    '''
                    d_str_list=d_str.split("','")
                    for d in d_str_list:
                        if d in phrase:
                            tag_error='y'
        custom_filter='y'
        '''
        if tag_error=='n':
            if custom_filter !='n':
                with open('../knol/custom_filter_word.json', 'r') as f_custom:
                    custom_filter_word= json.load(f_custom)
                for k in custom_filter_word.keys():
                    if k == semantic:
                        for word in custom_filter_word[k]:
                            pattern=re.compile(r'%s'%word,re.I)
                            result=pattern.findall(phrase)
                            if result!=[]:
                                custom_judge ='y'
       '''
    if filter_judge=='n':#保留
        if tag_error=='n' and custom_judge=='n':
            filter_result=False
    #print(filter_judge,tag_error,custom_judge,filter_result)
    return filter_result

def entity_filter(anno_result,Nsem):
    '''
    If the entity is finally retained, return False
    '''
    Nsemlist=[Nsem[i][1] for i in Nsem]
    manual_filter_path='../filter/'
    filter_dict={}
    filter_judge={}
    with open(manual_filter_path+'filter_a.csv',encoding='utf-8') as csvfile:
        reader=csv.reader(csvfile)
        for row in reader:
            if row[0]!='factor' and row[0] in Nsemlist: 
                filter_type=row[1]
                filter_data=pd.read_csv(manual_filter_path+row[0]+'/'+filter_type+'.csv')['name'].values.tolist()
                error_data=pd.read_csv(manual_filter_path+row[0]+'/error.csv',index_col=0)
                filter_judge[row[0]]=filter_type
                '''
                if error_data.shape[0]==0:
                    filter_dict[row[0]]={filter_type:filter_data,'error':''}
                '''
                filter_dict[row[0]]={filter_type:filter_data,'error':error_data}
                
    #anno_result=pd.DataFrame(anno_result,columns=['pmid','location','raw_text','CUI','metamap_word','normalization','semantic','sen_id','phrase'])
    anno_result_f=[]
    for anno in anno_result:
        semantic=anno[6].split(';')
        nor=anno[5]
        metamap_word=anno[4]
        phrase=anno[-1]
        filter_result=False
        for abbr in semantic:
            sem=Nsem[abbr][1]
            if sem in filter_dict:
                judge=filter_judge[sem]
                fdata=filter_dict[sem][judge]
                error_data=filter_dict[sem]['error']
                filter_result=get_filter_result(nor,metamap_word,semantic,phrase,judge,fdata,error_data)
                if filter_result:
                    break
        if filter_result==False:
            anno_result_f.append(anno[:-1])
    return anno_result_f
    

def save_anno(case,save_path,Nsem,metamap_filter=False):
    file_list=glob.glob(f"../case/{case}/MetaMap/out/{case}.metamap*.txt")
    print('The number of metamap output files[JSON format]:',len(file_list))
    print('JSON file format is being converted to list...')
    print('[MetaMap bioclist save path]:', save_path)
    with open(f'{save_path}metamap_anno.txt','w',encoding='utf-8') as fw,open(f'{save_path}metamap_sent.txt','w',encoding='utf-8') as fw1:
        fw.write('\t'.join(['pmid','location','raw_text','CUI','metamap_word',
                            'normalization','semantic','sen_id'])+'\n')
        fw1.write('\t'.join(['pmid','sen_id','sentence'])+'\n')
        sent_id_dic={}
        num=0
        for file in file_list:
            print('\tConverting:',file)
            with open(file,encoding='utf-8') as fp:
                json_content = json.load(fp)
            sent_result,anno_result=json_to_list(Nsem,json_content)
            for sent in sent_result:
                fw1.write('\t'.join(sent)+'\n')
                sent_id_dic[sent[1]]=0
            for anno in anno_result:
                if anno[-2] not in sent_id_dic:
                    num+=1
                    continue
                fw.write('\t'.join(anno[:-1])+'\n')
    if metamap_filter:
        print('Semantic filter is running...')
        print('[filter result save path]:', save_path)
        anno_result=entity_filter(anno_result,Nsem)
        with open(f'{save_path}metamap_anno_filter.txt','w',encoding='utf-8') as fw:
            fw.write('\t'.join(['pmid','location','raw_text','CUI','metamap_word',
                            'normalization','semantic','sen_id'])+'\n')
            for anno in anno_result:
                fw.write('\t'.join(anno)+'\n')
            
    #print('the number of sentences not in sen_id_dic:',num)

def get_semantic_info(semantic_select_file):
    semantic_dic={}
    semantic_select=[]
    with open(semantic_select_file,encoding='utf-8') as fp:
        semantic_select=fp.read().strip().split('\n')
    with open('../knol/Semantic/semantic_id.txt',encoding='utf-8') as fp:
        for line in fp:
            line=line.strip().split('|')
            if line[0] not in semantic_select:
                continue
            v2=line[2].replace(' ','_')
            v2=line[2].replace('-','_')
            v2=line[2].replace(',','_')
            semantic_dic[line[0]]=[line[2],v2]
    return semantic_dic
            


def main(argv):
   # parse parameters
    # 创建解析器对象
    parser = argparse.ArgumentParser(description='Entity processing tool')

    # 添加参数
    parser.add_argument('-c', '--case', type=str, required=True, help='Specify the case name')
    parser.add_argument('-f', '--filter',action='store_true', help='Using the semantic filter; if -f is not included, it defaults to False.')
    
    # 解析参数
    args = parser.parse_args()
    # 访问参数
    case=args.case
    metamap_filter=args.filter
    semantic_select_file='../knol/Semantic/semantic_select.txt'
    Nsem=get_semantic_info(semantic_select_file)
    save_path=f'../case/{case}/MetaMap/'
    save_anno(case,save_path,Nsem,metamap_filter)
    print('done')


if __name__ == "__main__":
    main(sys.argv[1:])
