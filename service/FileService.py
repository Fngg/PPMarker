import os
from pandas import read_table,read_excel
import numpy as np


def readFile(file_path, if_zero_na,usecols=None, index_col=0,header=0,**kwargs):
    if if_zero_na:
        na_values = ["Filtered", "NA", "","0", "#N/A","NAN","NULL"]
    else:
        na_values = ["Filtered", "NA", "", "#N/A", "NAN", "NULL"]
    if os.path.exists(file_path):
        # 获取文件后缀名
        file_type = os.path.splitext(file_path)[-1]
        if file_type in [".txt", ".tsv"]:
            df = read_table(file_path,
                               sep="\t",
                               header=header,
                               na_values=na_values,
                               usecols=usecols,
                               index_col=index_col,low_memory=False,**kwargs
                               )
        elif file_type == ".csv":
            df = read_table(file_path,
                               sep=",",
                               header=header,
                               na_values=na_values,
                               usecols=usecols,
                            index_col=index_col,low_memory=False,**kwargs
                               )
        elif file_type in [".xlsx", ".xls"]:
            df = read_excel(
                file_path,
                header=header,
                usecols=usecols,
                na_values=na_values,
                index_col=index_col,**kwargs
            )
        else:
        #     引发输入文件类型异常
            raise TypeError(f"该`{file_type}`文件类型不支持，仅支持【txt、csv、tsv、xlsx、xls】格式文件")
        if if_zero_na:
            df.replace(0, np.nan,inplace=True)
        return df
    else:
        raise FileNotFoundError("文件不存在"+file_path)