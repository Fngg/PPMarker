import util.Global as gol
import os
from service.FileService import readFile


def isNotEmpty(string):
    if string is not None and len(string.strip()) > 0:
        return True
    return False


def check_group():
    # groups ：只有在四个及其以上 group ： "B" , "M" ,"H" ,"QC" ，才需要填，必须选其中三个 ，比如 "M" ,"H" ,"QC" 或者 "B" ,"H" ,"QC" 或者 "B" ,"M" ,"QC"
    sampleInformationData = gol.get_value("SampleInformationData")
    if sampleInformationData is not None:
        groups = sampleInformationData['group'].unique()
        return groups
    return []


def get_group_list(filename):
    file = gol.get_value(filename)
    if os.path.exists(file):
        df = readFile(file,if_zero_na=False)
        groups = df['group'].unique()
        return groups
    return []

def get_column_list(file):
    if os.path.exists(file):
        df = readFile(file,if_zero_na=False,index_col=None)
        return df.columns.to_list()
    return []

def judge_correlation(file_path,ngroup,pgroup):
    if os.path.exists(file_path):
        df = readFile(file_path,if_zero_na=False)
        ngroup_samples = df.loc[df["group"]==ngroup,"name"].to_list()
        pgroup_samples = df.loc[df["group"]==pgroup,"name"].to_list()
        if len(ngroup_samples)==len(pgroup_samples):
            return True,ngroup_samples,pgroup_samples
    return False,None,None


def adaptive_font_size(num_columns,ticks_font_size,col_list):
    font_size = int(ticks_font_size*30/num_columns)
    col_max_len = 10 # 列名的长度，当列名越长时标题的字体越小
    for col in col_list:
        if len(col)>col_max_len:
            col_max_len=len(col)
    font_size = int(font_size*10/col_max_len)
    font_size = min(font_size,ticks_font_size)
    return max(10,font_size)