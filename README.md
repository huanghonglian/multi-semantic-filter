## Multi-semantic entity recognition and filter usage tutorial

The purpose of semantic filter is to remove false positive results of metamap recognition and improve the accuracy of entity recognition.

Download package: <a href="http://www.biomedinfo.cn:8281/static/download/multi-semantic_filter.zip">semantic_filter.zip</a>

#### Metamap installation

Before using the our semantic filter, you need to install the MetaMap tool.  

For installation instructions for MetaMap, please refer to:  

https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/Installation.html#metamap-installation. 

https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/run-locally/MainDownload.html.


```python
#Add environment variable
#Replace 'zh' in the command line with your username
echo 'export PATH="/home/zh/public_mm/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### step 1. Literature retrieval

For each case, we obtained its standard expression term and synonyms from MeSH database, then used these terms to retrieved PubMed database and get the relevant PubMed identifiers (PMIDs). 

For a simple example case named 'test', we curate the search term in PubMed.gov, and save as _../case/test/test.term.txt_.


```python
((Stomach Neoplasm[Title/Abstract]) OR (Gastric Cancer[Title/Abstract])) AND 
(((Herpesvirus 4, Human[Title/Abstract]) OR (Epstein Barr Virus[Title/Abstract])) OR (EBV[Title/Abstract]))
```

Run following code to obtain pmid and abstract in medline format:


```python
cd lib
python medline_download.py -c test
```

The results are saved as _../case/test/test.pmid.txt_ and _../case/MEDLINE/*_.  To streamline subsequent entity recognition, we will split the PMIDs into files of 10,000 each.

#### step 2. Multi-semantic entity recognition

MetaMap is a highly configurable application developed by the Lister Hill National Center for Biomedical Communications at the National Library of Medicine (NLM) to map biomedical text to the UMLS Metathesaurus or, equivalently, to identify Metathesaurus concepts referred to in English text. The UMLS is a comprehensive biomedical vocabulary that includes over 3.3 million biomedical concepts from more than 200 different source vocabularies and defines 127 semantic types. In this study, we selected 43 semantic types related to viral carcinogenesis from these 127 semantic types. These 43 semantic types were divided into 38 external factors and 5 internal factors based on their biological significance

For detailed descriptions of the 127 semantic types, please refer to:  
https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html

If you wish to recognize entities of other semantic types, you can modify the _./knol/Semantic/semantic_select.txt_ file. Please note that the file should only contain abbreviations of semantic types, with each abbreviation on a separate line.


```python
python metamap.py -c test
```

The results are saved as _./case/test/out/*_. The terminal output of the identification process is recorded in _./case/test/log/*_.

#### step 3. Improve accuracy with semantic filter

Semantic filters are used to remove false positive entities resulting from metamap recognition.


```python
# For a case named test, we run step 1-3:
cd lib
python semantic_filter.py -c test -f
```

usage: semantic_filter.py [-h] -c CASE [-f]  

Entity processing tool  

options:  
&emsp;-h,&emsp;--help$~~~~~~~~~~~~~~~~~~~~~~$show this help message and exit  
&emsp;-c&emsp;CASE, --case CASE$~~~~$Specify the case name  
&emsp;-f,&emsp;--filter$~~~~~~~~~~~~~~~~~~~~~~$Using the semantic filter; if -f is not included, it defaults to False.  

The results with filter are saved in _./case/MetaMap/metamap_anno_filter.txt_, while the results without filter are in the  _./case/MetaMap/metamap_anno.txt_. Sentences are saved in./case/metamap/metamap_sent.txt

### Contacts

honglian_huang@163.com, Tongji University, Shanghai, 200092, China
