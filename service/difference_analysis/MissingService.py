import pandas as pd
from util.Logger import logger
import numpy as np
from missingpy import MissForest


def get_filter_name(df,filter_rate,axis=1):
    ''''
    过滤缺失值比例大于filter_rate的蛋白;axis=1时代表以行统计，为0时列统计；输出蛋白的名称列表
    '''
    if axis not in [0,1]:
        logger.warning("axis的值只能为0或1")
        return None
    if axis == 1:
        shape = df.shape[1]
    else:
        shape = len(df)
    missing_df = df.isnull().sum(axis=axis) / shape
    missing = list(missing_df[missing_df > float(filter_rate)].index)
    return missing


def filter(df,filter_rate,groups=None):
    '''
    过滤缺失值比例大于filter_rate的蛋白,当groups传入值时代表按照组别进行过滤，groups的值为[[],[]]
    :param df:
    :param groups: 分组情况，缺失值过滤是否按照组别分别过滤
    :return:
    '''
    if groups != None:
        # 按照组别过滤
        missing = []
        for group in groups:
            group_df = df[group]
            group_missing = get_filter_name(group_df,filter_rate)
            logger.debug(f"group：{group}\n,filter rows lens:{len(group_missing)},\nfilter rows :{group_missing}")
            missing.extend(group_missing)
        # 对missing进行去重
        filter_rows = list(set(missing))
        logger.debug(f'We will remove {len(filter_rows)} rows. they are {filter_rows}.')
        df1 = df.drop(filter_rows)
    else:
        # 统一过滤
        missing = get_filter_name(df,filter_rate)
        logger.debug(f'We will remove {len(missing)} rows. they are {missing}.')
        df1 = df.drop(missing)
    return df1


def get_filter_name_by_n(df,filter_n,axis=1):
    ''''
    过滤缺失值比例大于filter_rate的蛋白;axis=1时代表以行统计，为0时列统计；输出蛋白的名称列表
    '''
    if axis not in [0,1]:
        logger.warning("axis的值只能为0或1")
        return None
    if axis == 1:
        shape = df.shape[1]
    else:
        shape = len(df)
    not_missing_df = shape-df.isnull().sum(axis=axis)
    missing = list(not_missing_df[not_missing_df < filter_n].index)
    return missing


def get_filter_name_by_ratio(df,filter_ratio,axis=1):
    ''''
    过滤缺失值比例大于filter_rate的蛋白;axis=1时代表以行统计，为0时列统计；输出蛋白的名称列表
    '''
    if axis not in [0,1]:
        logger.warning("axis的值只能为0或1")
        return None
    if axis == 1:
        shape = df.shape[1]
    else:
        shape = len(df)
    not_missing_df = shape-df.isnull().sum(axis=axis)
    not_missing_df = not_missing_df/shape
    missing = list(not_missing_df[not_missing_df < filter_ratio].index)
    return missing


def filter_by_ratio(df,filter_ratio,groups):
    '''
    过滤掉各组中有缺失值比例大于filter_rate的蛋白
    '''
    missing = []
    for group in groups:
        group_df = df[group]
        group_missing = get_filter_name_by_ratio(group_df,filter_ratio)
        # logger.debug(f"group：{group}\n,filter rows lens:{len(group_missing)},\nfilter rows :{group_missing}")
        logger.debug(f"group：{group}\n,filter rows lens:{len(group_missing)}.")
        missing.extend(group_missing)
    # 对missing进行去重
    filter_rows = list(set(missing))
    logger.debug(f'We will remove {len(filter_rows)} rows.')
    df1 = df.drop(filter_rows)
    return df1

def filter_by_ratio_no_group(df,filter_ratio):
    '''
    过滤掉各组中有缺失值比例大于filter_rate的蛋白
    '''
    filter_rows = get_filter_name_by_ratio(df,filter_ratio)
    logger.debug(f'We will remove {len(filter_rows)} rows.')
    df1 = df.drop(filter_rows)
    return df1


def filter_by_n(df,filter_n,groups):
    '''
    过滤掉各组中有值的数量小于filter_n的蛋白，必须分组进行
    '''
    missing = []
    for group in groups:
        group_df = df[group]
        group_missing = get_filter_name_by_n(group_df,filter_n)
        # logger.debug(f"group：{group}\n,filter rows lens:{len(group_missing)},\nfilter rows :{group_missing}")
        # logger.debug(f"group：{group}\n,filter rows lens:{len(group_missing)}.")
        missing.extend(group_missing)
    # 对missing进行去重
    filter_rows = list(set(missing))
    logger.debug(f'We will remove {len(filter_rows)} rows.')
    df1 = df.drop(filter_rows)
    return df1


def get_special_missing_pros(data,groups_dict):
    if len(groups_dict)!=2:
        logger.warning("get_special_missing_pros只适用于两个组别")
        return None
    group1 = list(groups_dict.keys())[0]
    group2 = list(groups_dict.keys())[1]
    def is_special_missing_pro(data1,data2):
        result1 = data1.isnull().all()
        result2 = data2.isnull().all()
        if result1 and (not result2):
            return True
        else:
            return False
    data["is_special"] = data.apply(lambda row: is_special_missing_pro(row[groups_dict[group1]], row[groups_dict[group2]]), axis=1)
    return data


def base_missing_filing(data,groups=None):
    '''
    同样本蛋白质丰度最小有效值替换缺失值；数据表蛋白质丰度最小有效值替换缺失值；同组别对应蛋白质丰度最小有效值替换缺失值。一般采用第三种，在极端情况下同组别均为缺失值时采用第一种方式。
    :param df:
    :return:
    '''
    if groups is not None:
        df = pd.DataFrame()
        for i in range(len(groups)):
            group = groups[i]
            df1 = data[group]
            column_name = "min"+str(i)
            min_data = df1.min(axis=1, skipna=True)
            df1.insert(0, column_name, min_data)
            for column in df1.columns:
                if column != column_name:
                    df1[column].fillna(df1[column_name], inplace=True)
            df1.drop(column_name, axis=1, inplace=True)
            df = pd.concat([df,df1],axis=1)
    else:
        df = data.copy(deep=True)
        # df['min'] = df.min(axis=1,skipna=True)
        min_data = df.min(axis=1, skipna=True)
        df.insert(0, 'min', min_data)
        for column in df.columns:
            if column != "min":
                df[column].fillna(df["min"], inplace=True)
        df.drop('min', axis=1,inplace = True)
    indexs = df.isnull().T.any()
    missing_indexs = list(indexs[indexs == True].index)
    logger.warning(f"====格外关注：{missing_indexs}")
    columns = df.isnull().any()
    missing_columns = list(columns[columns == True].index)
    if len(missing_columns):
        # 以第三种方法填充过后还是存在null值
        logger.warning(f"====格外关注：{missing_columns}")
        for missing_column in missing_columns:
            df[missing_column].fillna(np.min(df[missing_column]),inplace=True)
    return df


def knn_missing_filter(df,n_neighbors=5):
    '''
    从样本方面训练，KNN算法进行缺失值填补，原理是基于目标样本的值与相邻样本的值相似
    :param df:
    :param groups: 样本分组列表
    :param n_neighbors:
    :return:
    '''
    from sklearn.impute import KNNImputer
    # 确定n_neighbors
    # df.shape[1] - max(df.isnull().sum(axis=1)) 有最多缺失值的蛋白的无缺失值数量
    n_neighbors1 = df.shape[1] - max(df.isnull().sum(axis=1))
    if n_neighbors1 < n_neighbors:
        n_neighbors = n_neighbors1
    logger.debug(f"knn从样本方面训练，n_neighbors：{n_neighbors}")
    imputer = KNNImputer(n_neighbors=n_neighbors)
    data = imputer.fit_transform(df.transpose())
    result_df = pd.DataFrame(data,index=df.columns,columns=df.index)
    return result_df.transpose()


# def knn_missing_filter(df,n_neighbors=5):
#     '''
#     KNN算法进行缺失值填补，原理是基于目标蛋白质的值与相邻蛋白质值相似  https://blog.csdn.net/sinat_33264502/article/details/108340942
#     :param df:
#     :return:
#     '''
#     from sklearn.impute import KNNImputer
#     imputer = KNNImputer(n_neighbors=n_neighbors)
#     data = imputer.fit_transform(df)
#     result_df = pd.DataFrame(data,index=df.index,columns=df.columns)
#     return result_df


def forest_missing_filing(df,n_trees=100):
    '''
    MissForest缺失值填补方法
    :param df:
    :param n_trees:
    :return:
    '''

    forestimp = MissForest(n_estimators=n_trees, random_state=123)
    data = forestimp.fit_transform(df)
    result_df = pd.DataFrame(data, index=df.index, columns=df.columns)
    return result_df