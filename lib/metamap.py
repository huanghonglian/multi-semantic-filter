#metamap识别
import os
import sys
import glob
import getopt


def run_metamap(case,save_path=None):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    log_path=save_path+'log/'
    out_path=save_path+'out/'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    file_list=glob.glob(f"../case/{case}/MEDLINE/{case}.medline*.txt")
    print("[case]: {},[save path]:{}".format(case, save_path))
    # 分批处理
    for file in file_list:
        p=file.index('medline')
        name_index=file[p+7:-4]
        print(f'\tMetaMap:{file}')
        command=f'metamap -y  --JSONn {file}  {out_path}{case}.metamap{name_index}.txt >{log_path}{case}.metamap{name_index}.log 2>&1'
        run_metamap=os.system(command)
        



def main(argv):
    # parse parameters
    case = ''
    try:
        opts, args = getopt.getopt(argv, "hc:", ["case="])
    except getopt.GetoptError:
        print('python metamap.py -c <case>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python metamap.py -c <case>')
            sys.exit()
        elif opt in ("-c", "--case"):
            case = arg
    # obtain pmid, pmcid
    #pmid_file = os.path.join(f'../case/{case}', f'{case}.pmid.txt')
    #pmcid_file = os.path.join(f'../case/{case}', f'{case}.pmcid.txt')
    print('Entity recognition by MetaMap will take some time...')
    save_path=f'../case/{case}/MetaMap/'
    run_metamap(case,save_path)
            
            

if __name__ == "__main__":
    main(sys.argv[1:])