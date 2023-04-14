import numpy as np


def quantile_norm(df):
    '''
    分位数校正，https://cmdlinetips.com/2020/06/computing-quantile-normalization-in-python/amp/
    :param df:
    :return:
    '''
    from qnorm import quantile_normalize
    # 按列来校正
    df_qn = quantile_normalize(df)
    # 可视化
    return df_qn


def flatten_sum_norm(df):
    '''
    样本和的中位数校正：计算每个样本的蛋白总量，再算出所有样本各自蛋白总量的中位数，再将中位数除以每个样本的蛋白总量，作为每个样本的校正因子，将每个样本中的每个蛋白的表达量乘以校正因子，作为校正的结果。
    '''
    cols_sum = df.sum(axis=0)
    median_sum = np.median(cols_sum)
    factor_sum = median_sum/cols_sum
    df_qn = df.mul(factor_sum, axis=1)
    return df_qn


def FOT_norm(df):
    '''
    经过iBAQ校正之后样本内不同蛋白的表达量也可以进行比较，这时候再使用FOT校正方法，FOT校正方法是将每个样本中每个蛋白的值除以该样本中所有蛋白的总和，这样所有样本的蛋白总和都是1
    '''
    df_norm = df / df.sum(axis=0)
    return df_norm


def upper_quantile_norm(df):
    upper_quantile = df.quantile(q=0.75)
    # 用各列的值除以对应的上四分位数
    tmp_df = df.div(upper_quantile,axis=1)
    # 每个值都乘以 upper_quantile 的均值
    mean_upper_quantile = upper_quantile.mean()
    df_qn = tmp_df.applymap(lambda x: x*mean_upper_quantile)
    return df_qn


def ratio(df,information_df,qcgroup):
    '''
    行校正
    df: 表达矩阵
    information_df： 样本信息表
    qcgroup： 质控组
    '''
    df1 = df.copy()
    batchs = information_df["batch"].unique()
    for batch in batchs:
        qc = information_df.loc[(information_df['batch']==batch)&(information_df['group']==qcgroup),"name"].iloc[0]
        indexs = information_df.loc[(information_df['batch']==batch)&(information_df['group']!=qcgroup),"name"]
        for index in indexs:
            df1[index] = df1[index] / df1[qc]
    return df1