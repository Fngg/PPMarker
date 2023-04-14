'''
检测导入的数据是否符合规定的格式
'''
import os
import pandas as pd
import util.Global as gol
from util.Logger import logger
from config.global_config import software_name,Quality_Assessment_dirname,Normalization_and_Filtering_dirname,Difference_Analysis_dirname,Enrichment_Analysis_dirname


def check_data_label_free_pro(expression_df, information_df):
    '''
    检测导入的样本信息表是否包含id	name	group	order	batch列;
    检测表达数据中是否包含“Gene names列和“样本信息表中id列对应的所有值”的列
    '''
    if {'id', 'name', "group"}.issubset(information_df.columns):
        # if "Gene names" in expression_df.columns:
        if set(information_df["id"]).issubset(expression_df.columns):
            return True,None
        else:
            return False, "表达数据中缺少与'样本信息表中id列对应的所有值'的列。"
        # else:
        #     return False, "表达数据中缺少'Gene names'对应的列。"
    else:
        return False,"样本信息表中缺少'id','name','group'对应的列。"


def check_data_marked_pro(expression_df, information_df):
    '''
    检测导入的样本信息表是否包含id	name	group	order	batch列;
    检测表达数据中是否包含“Gene names列和“样本信息表中id列对应的所有值”的列
    '''
    if {'id', 'name', "group", "batch"}.issubset(information_df.columns):
        if not information_df["batch"].isnull().any():
            if set(information_df["id"]).issubset(expression_df.columns):
                return True,None
            else:
                return False, "表达数据中缺少与'样本信息表中id列对应的所有值'的列。"
        else:
            return False, "样本信息表中'batch'对应的列不能有空值。"
    else:
        return False,"样本信息表中缺少'id','name','group','batch'对应的列。"


def check_data_label_free_pho(expression_df, information_df,pro_dfp_df,pro_supplementary_df):
    '''
    无标记的磷酸化组学数据检测
    对蛋白质组学差异表达结果的检测，第一个sheet中应包含Pvalue	log2FC	FoldChange(FC)这三列，第二个sheet中除了索引，必须还有其他列，代码中是根据第一列与磷酸化组学的数据进行比对
    '''
    if {'id', 'name', "group"}.issubset(information_df.columns):
        if set(information_df["id"]).issubset(expression_df.columns):
            # 对蛋白质组学差异表达结果的检测
            if {"Pvalue","DEP","FoldChange(FC)"}.issubset(pro_dfp_df.columns):
                if pro_supplementary_df.shape[1]>=1:
                    return True,None
                else:
                    return False, "蛋白质组学差异表达结果的第二个sheet中缺少与磷酸化组对应的信息。"
            else:
                return False,"蛋白质组学差异表达结果的第一个sheet中缺少Pvalue	log2FC	FoldChange(FC)这三列。"
        else:
            return False, "表达数据中缺少与'样本信息表中id列对应的所有值'的列。"
    else:
        return False,"样本信息表中缺少'id','name','group'对应的列。"


def check_data_marked_pho(expression_df, information_df,pro_dfp_df,pro_supplementary_df):
    '''
    无标记的磷酸化组学数据检测
    对蛋白质组学差异表达结果的检测，第一个sheet中应包含Pvalue	log2FC	FoldChange(FC)这三列，第二个sheet中除了索引，必须还有其他列，代码中是根据第一列与磷酸化组学的数据进行比对
    '''
    if {'id', 'name', "group", "batch"}.issubset(information_df.columns):
        if not information_df["batch"].isnull().any():
            if set(information_df["id"]).issubset(expression_df.columns):
                # 对蛋白质组学差异表达结果的检测
                if {"Pvalue","DEP","FoldChange(FC)"}.issubset(pro_dfp_df.columns):
                    if pro_supplementary_df.shape[1]>=1:
                        return True,None
                    else:
                        return False, "蛋白质组学差异表达结果的第二个sheet中缺少与磷酸化组对应的信息。"
                else:
                    return False,"蛋白质组学差异表达结果的第一个sheet中缺少Pvalue	log2FC	FoldChange(FC)这三列。"
            else:
                return False, "表达数据中缺少与'样本信息表中id列对应的所有值'的列。"
        else:
            return False, "样本信息表中'batch'对应的列不能有空值。"
    else:
        return False,"样本信息表中缺少'id','name','group','batch'对应的列。"


def create_result_dir(result_path,if_enrich=False):
    folder1 = os.path.join(result_path,Quality_Assessment_dirname)
    if not os.path.exists(folder1):
        os.makedirs(folder1)
    folder2 = os.path.join(result_path, Normalization_and_Filtering_dirname)
    if not os.path.exists(folder2):
        os.makedirs(folder2)
    folder3 = os.path.join(result_path, Difference_Analysis_dirname)
    if not os.path.exists(folder3):
        os.makedirs(folder3)
    if if_enrich:
        folder4 = os.path.join(result_path, Enrichment_Analysis_dirname)
        if not os.path.exists(folder4):
            os.makedirs(folder4)
        up_folder = os.path.join(folder4, "up")
        if not os.path.exists(up_folder):
            os.makedirs(up_folder)
        down_folder = os.path.join(folder4, "down")
        if not os.path.exists(down_folder):
            os.makedirs(down_folder)


def get_groups_dict_list(simple_information):
    '''
    groups_dict = {"A":[,,,],"B":[,,,]}
    groups = [[,,,],[,,,]]
    simple = [,,,,,,]
    '''
    groups_dict={}
    for i in simple_information.index:
        group_name = simple_information.loc[i,"group"]
        if group_name not in list(groups_dict.keys()):
            groups_dict[group_name]= [simple_information.loc[i,"name"]]
        else:
            groups_dict[group_name].append(simple_information.loc[i,"name"])
    groups = list(groups_dict.values())
    return groups_dict,groups,list(simple_information["name"])


def export_data(df1,result_dir,sub_dir,file_name,sheet_name1,df2=None,sheet_name2=None):
    '''
    输出excel文件
    定义样式参考这个https://www.jianshu.com/p/1b003978e12a
    '''
    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None
    file_path = os.path.join(result_dir,sub_dir,file_name)
    with pd.ExcelWriter(file_path) as writer:
        df1.to_excel(writer, sheet_name=sheet_name1)  # Sheet1
        if df2 is not None:
            if sheet_name2 is None:
                sheet_name2 = "supplementary data"
            df2.to_excel(writer, sheet_name=sheet_name2)  # Sheet2


def get_color_list(groups_dict,colors):
    if groups_dict is None or len(groups_dict) > len(colors):
        logger.warning("groups_dict的长度大于colors的长度，设置默认的颜色")
        import palettable
        return palettable.tableau.TrafficLight_9.mpl_colors
    result_list = []
    simples = []
    groups = list(groups_dict.values())
    for i in range(len(groups)):
        simples.extend(groups[i])
        result_list.extend([colors[i]]*len(groups[i]))
    return result_list,simples


def group_dict_to_simple_dict(groups_dict,if_label=False):
    '''
    将{"A":[,,,],"B":[,,,]}转为{"simple1":0,"simple2":1,...}
    if_label为False时输出的dict的value是0，1，2.。。。
    if_label为True时输出的dict的value是对应的label
    '''
    result = {}
    labels = list(groups_dict.keys())
    for i in range(len(groups_dict)):
        key = labels[i]
        for j in groups_dict[key]:
            if if_label:
                result[j] = key
            else:
                result[j] = i
    return result


def extract_gene_name(expression_df):
    '''
    对于PD软件的数据文件中没有 ”Gene names“ 的列，需要从 Description 列中提取
    '''
    if "Gene names" not in expression_df.columns and "Description" in expression_df.columns:
        def get_gene_name(description):
            try:
                split1 = description.split("GN=")
                split2 = split1[1].split()
                return split2[0]
            except:
                logger.info(f"异常的description:{description}")
                return ""
        expression_df["Gene names"] = expression_df.apply(lambda row: get_gene_name(row["Description"]), axis=1)
    return expression_df


def get_tmp_dir():
    root_path = gol.get_value("RootPath")
    dir_path = os.path.join(root_path, "tmp")
    return dir_path