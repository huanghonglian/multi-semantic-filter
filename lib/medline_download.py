# *_* coding: utf-8 *_*
# @Time     : 10/11/2021 12:59 PM
# @Author   : zong hui
# @object   : some useful functions related to PubMed.gov database

"""
功能主要包括：
    term_to_pmid:          输入查询词，访问PubMed数据库，获得PMID列表。
    parse_PMCIDsFile:      解析PubMed数据库的ID映射文件，获得PMID和PMCID的映射。
    pmid_to_pmcid:         输入pmid列表，获取对应的pmcid。
    download_medline:      输入pmid列表，下载Medline格式数据。
"""


import os
import sys
import csv
import json
import time
import getopt
import requests
import pandas as pd
from Bio import Medline, Entrez
Entrez.email = ""


def term_to_pmid(term_file: str, save_path=None) -> list:
    """输入查询词，访问PubMed数据库，获得PMID列表."""
    # 构建查询语句
    with open(term_file, 'r') as f:
        term = f.readline().strip('\n')
    print(f'[search term]: {term}')
    # 开始检索
    handle0 = Entrez.esearch(db='pubmed', term=term, RetMax=300000000)
    record = Entrez.read(handle0)
    pmids, count = record['IdList'], record['Count']
    print(len(pmids))
    # 按升序进行排序
    #pmids.sort(key=int)
    # 保存结果
    if save_path:
        with open(save_path, 'w') as f:
            f.write('PMID\n')
            f.write('\n'.join(pmids) + '\n')
    print(f'[pmid]: {len(pmids)}, [save path]: {save_path}')
    return pmids


def parse_PMCIDsFile(pmcids_file = "../knol/PubMed/PMC-ids.csv"):
    """
    The PMC-ids.csv.gz file, available through the FTP service,
    maps an article’s standard IDs to each other and to other article metadata elements.
    PMC-ids.csv.gz is a comma-delimited file with the following fields:
    Journal Title, ISSN, ..., PMCID, PubMed ID (if available), ..., Release Date (Mmm DD YYYY or live)
    link: https://www.ncbi.nlm.nih.gov/pmc/pmctopmid/
    """
    pmcid2pmid = dict()
    pmid2pmcid = dict()
    print(f'loading {pmcids_file}, please waiting...')
    with open(pmcids_file, 'r') as inf:
        rows = list(csv.reader(inf))
        for row in rows[1:]:
            pmcid2pmid[row[8]] = row[9]
            if row[9]:
                pmid2pmcid[row[9]] = row[8]
    print(f'{len(pmcid2pmid)} pmcid mapped to {len(pmid2pmcid)} pmid in file PMC-ids.csv.gz')
    return pmcid2pmid, pmid2pmcid


def pmid_to_pmcid(pmids: list, pmid2pmcid: dict, save_path=None):
    """输入PMID，获得相应的PMCID"""
    pmcids = [pmid2pmcid.get(p, '') for p in pmids]
    pmcids_count = len(pmcids) - pmcids.count('')
    if save_path:
        with open(save_path, 'w') as f:
            f.write('PMID\tPMCID\n')
            for pmid, pmcid in zip(pmids, pmcids):
                f.write('{}\t{}\n'.format(pmid, pmcid))
        print(f'[pmcid]: {pmcids_count}, [save path]: {save_path}')
    return pmcids


def download_medline(case, pmids:list=None, save_path=None):
    t1 = time.time()
    # 如果存储路径不存在，则创建
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    print("[case]: {}, [pmid]: {}, [save path]:{}".format(case, len(pmids), save_path))
    # 分批次下载，每次下载10000条
    count = len(pmids)
    batch_size = 10000
    iterations = [[i * batch_size, min((i + 1) * batch_size, count)] for i in range((count-1) // batch_size + 1)]
    # 开始分批次下载
    for (start, end) in iterations:
        # 获取数据，Medline格式
        handle = Entrez.efetch(db='pubmed', id=pmids[start:end], rettype='medline', retmode='text')
        try:
            records=handle.read()
            cur_save_path = os.path.join(save_path, "{}.medline_{}-{}.txt".format(case,start, end+1))
            with open(cur_save_path,'w',encoding='utf-8') as f:
                f.write(records)
            print('\t[Downloading]: {}-{}'.format(start, end+1))
            # 休眠1秒，避免持续访问导致连接中断
            time.sleep(1)
        except:
            print('not download:',start,end+1)
            continue
    t2 = time.time()
    print('\t[used time]: {} seconds.'.format(round(t2-t1, 4)))
    return "downloaded!"


def main(argv):
    # parse parameters
    case = ''
    try:
        opts, args = getopt.getopt(argv, "hc:", ["case="])
    except getopt.GetoptError:
        print('python medline_download.py -c <case>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python medline_download.py -c <case>')
            sys.exit()
        elif opt in ("-c", "--case"):
            case = arg
    # obtain pmid, pmcid
    term_file = os.path.join(f'../case/{case}', f'{case}.term.txt')
    pmid_file = os.path.join(f'../case/{case}', f'{case}.pmid.txt')
    #pmcid_file = os.path.join(f'../case/{case}', f'{case}.pmcid.txt')
    #pmcid2pmid, pmid2pmcid = parse_PMCIDsFile()
    pmids = term_to_pmid(term_file, save_path=pmid_file)
    with open(pmid_file,encoding='utf-8') as fp:
        pmids=fp.read().strip().split('\n')[1:]
    #pmcids = pmid_to_pmcid(pmids, pmid2pmcid, save_path=pmcid_file)
    save_path=f'../case/{case}/MEDLINE/'
    download_medline(case,pmids,save_path)

if __name__ == "__main__":
    main(sys.argv[1:])

