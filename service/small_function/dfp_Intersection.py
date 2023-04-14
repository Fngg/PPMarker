### 两个差异分析结果求交集
import pandas as pd

from service.FileService import readFile
from util.Logger import logger


def read_dfp_file(dfp_file_path):
    supplementary_df = readFile(dfp_file_path,if_zero_na=False,sheet_name=1,usecols=["Gene names_No.","Gene names"])
    if "Gene names" in supplementary_df.columns:
        df = readFile(dfp_file_path,if_zero_na=False,sheet_name=0,usecols=["Gene names_No.","DEP"])
        up_indexes = df.loc[df["DEP"]=="up-regulated"].index
        down_indexes = df.loc[df["DEP"]=="down-regulated"].index
        dfp_indexes = df.loc[df["DEP"]!="none-significant"].index
        up_genes = supplementary_df.loc[up_indexes,"Gene names"].to_list()
        down_genes = supplementary_df.loc[down_indexes,"Gene names"].to_list()
        dfp_genes = supplementary_df.loc[dfp_indexes,"Gene names"].to_list()
        return up_genes,down_genes,dfp_genes
    else:
        logger.error("supplementary data中没有Gene names列无法比较")
        return [],[],[]


def intersection(dfp_file_path1,dfp_file_path2,output_path):
    up_genes1,down_genes1,dfp_genes1 = read_dfp_file(dfp_file_path1)
    up_genes2,down_genes2,dfp_genes2 = read_dfp_file(dfp_file_path2)
    up_inter = list(set(up_genes1).intersection(set(up_genes2)))
    down_inter = list(set(down_genes1).intersection(set(down_genes2)))
    dfp_inter = list(set(dfp_genes1).intersection(set(dfp_genes2)))
    result = pd.DataFrame()
    up_inter.extend([""]*(len(dfp_inter)-len(up_inter)))
    down_inter.extend([""]*(len(dfp_inter)-len(down_inter)))
    result["up_intersection"] = up_inter
    result["down_intersection"] = down_inter
    result["dfp_intersection"] = dfp_inter
    result.to_csv(output_path,index=False)


if __name__=="__main__":
    dfp_file_path1 = "C:/Users/aohan/Project/iris/组学软件测试/丁一师姐/分析/N_T_remove/3-Difference_Analysis_Results/difference_analysis.xlsx"
    dfp_file_path2 = "C:/Users/aohan/Project/iris/组学软件测试/丁一师姐/分析/MT_MN_remove/3-Difference_Analysis_Results/difference_analysis.xlsx"
    output_path = "C:/Users/aohan/Project/iris/组学软件测试/丁一师姐/分析/intersection.csv"
    intersection(dfp_file_path1, dfp_file_path2, output_path)
