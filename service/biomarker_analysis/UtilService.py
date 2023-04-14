import os
import pandas as pd
import numpy as np
from util.Logger import logger

from service.FileService import readFile
from service.difference_analysis.DropConRevService import drop_CON_REV
from service.difference_analysis.MissingService import filter_by_n, base_missing_filing, knn_missing_filter, \
    forest_missing_filing
from service.difference_analysis.NormalizationService import upper_quantile_norm, quantile_norm, ratio, \
    flatten_sum_norm, FOT_norm
from service.difference_analysis.UtilService import extract_gene_name, check_data_label_free_pro, get_groups_dict_list, \
    export_data, check_data_marked_pro
from service.biomarker_analysis.DatasetSplitService import get_class
from config.global_config import software_name,biomarker_model_dirname,biomarker_data_split_dirname,biomarker_feature_select_dirname,biomarker_preprocess_dirname


def create_result_dir(result_path):
    folder1 = os.path.join(result_path,biomarker_preprocess_dirname)
    if not os.path.exists(folder1):
        os.makedirs(folder1)
    folder2 = os.path.join(result_path, biomarker_feature_select_dirname)
    if not os.path.exists(folder2):
        os.makedirs(folder2)
    folder3 = os.path.join(result_path, biomarker_data_split_dirname)
    if not os.path.exists(folder3):
        os.makedirs(folder3)
    folder4 = os.path.join(result_path, biomarker_model_dirname)
    if not os.path.exists(folder4):
        os.makedirs(folder4)


def handle_test_data(test_data_path,test_information_path,result_path,dirname,ngroup,pgroup,final_select_proteins,qcgroup=None,log2=True):
    '''
    处理新的测试集数据：缺失值填值
    '''
    test_data_df = readFile(test_data_path, index_col=None,if_zero_na=True)
    information_df = readFile(test_information_path, index_col=None,if_zero_na=False)
    group_num = information_df["group"].nunique()
    # 检测数据是否符合要求
    if group_num==3 and qcgroup is not None:
        # 标记定量
        result, despri = check_data_marked_pro(test_data_df, information_df)
    else:
        result, despri = check_data_label_free_pro(test_data_df, information_df)
    if not result:
        return None,despri
    test_data_df = extract_gene_name(test_data_df)
    if "Gene names" not in test_data_df.columns:
        return None,"导入的新的测试集数据中没有Gene names列"
    test_data_df["Gene names"].fillna("", inplace=True)
    test_data_df.drop_duplicates(subset="Gene names",keep='first',inplace=True)
    test_data_df.index = test_data_df["Gene names"]

    # 确定下生物标志物蛋白在新的数据集中是否全部都有
    final_select_proteins_test = []
    final_select_proteins_index = []
    not_exist_select_proteins_test = []
    for protein in  final_select_proteins:
        new_p = protein.replace("_"+protein.split("_")[-1],"")
        if new_p in test_data_df.index:
            final_select_proteins_test.append(new_p)
            final_select_proteins_index.append(protein)
        else:
            not_exist_select_proteins_test.append(protein)
    if len(final_select_proteins_test)==0:
        return None, "在新的独立测试集中没有筛选出的生物标志物的表达信息"
    test_data_df = test_data_df.loc[final_select_proteins_test,information_df["id"]]
    test_data_df.columns = information_df["name"]
    test_data_df.index = final_select_proteins_index
    groups_dict, groups, simples = get_groups_dict_list(information_df)

    # 行校正
    if qcgroup is not None and group_num==3:
        expression_norm_df = ratio(test_data_df, information_df, qcgroup)
        # 删除质控组
        qcgroup_names = list(information_df.loc[information_df["group"] == qcgroup, "name"])
        expression_norm_df.drop(columns=qcgroup_names, inplace=True)
        information_df = information_df[information_df['group']!=qcgroup]
        groups_dict, groups, simples = get_groups_dict_list(information_df)
    else:
        expression_norm_df = test_data_df

    expression_imputation_df = base_missing_filing(expression_norm_df, groups=groups)

    if log2 and (not (expression_imputation_df < 0).values.any()):
        # 再取log2的时候需要保证全部的值都要大于0
        expression_imputation_df = expression_imputation_df.applymap(lambda x: np.log2(x))
    export_data(expression_imputation_df, result_path, dirname,
                "pretreated_new_test_data.xlsx", "new_test_data")

    data = pd.DataFrame(expression_imputation_df.values.T, index=expression_imputation_df.columns, columns=expression_imputation_df.index)
    data["class"] = data.apply(lambda row: get_class(row.name, groups_dict[ngroup], groups_dict[pgroup]), axis=1)

    X_test_prepared = data.drop("class", axis=1)
    y_test = data["class"].copy()

    return (X_test_prepared,y_test,final_select_proteins_index,not_exist_select_proteins_test),""



