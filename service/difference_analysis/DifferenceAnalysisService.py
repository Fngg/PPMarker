# 差异分析
import numpy as np
import pandas as pd
from scipy import stats
from util.Logger import logger


def sub_dfp_analysis(data1,data2):
    '''
    这里log2FC用的是一组重复样本的平均值
    首先 Shapiro-Wilk正态检验方法来检验样本是否符合正态分布；
    :param data1: 一组样本的值
    :param data2: 一组样本的值
    :return:
    '''
    # 如果data1和data2中有nan要去掉
    data1 = data1[data1.notnull()]
    data2 = data2[data2.notnull()]
    # 将data1和data2拼接起来进行正态分布分析
    isnormal_statistic,isnormal_pvalue = stats.shapiro(data1.append(data2))
    try:
        if isnormal_pvalue > 0.05:
            # 符合正态性分布
            # 再检查方差齐性，levene检验
            levene_statistic, levene_pvalue = stats.levene(data1, data2)
            if levene_pvalue >0.05:
                # 两组样本具有方差齐性，采用t检验
                ttest_statistic,ttest_pvalue = stats.ttest_ind(data1, data2)
            else:
                # 两组样本不具有方差齐性，采用welch's T检验
                ttest_statistic, ttest_pvalue = stats.ttest_ind(data1, data2,equal_var = False)
            return ttest_pvalue
        else:
            # 不符合正态性分布，采用秩和检验进行差异分析
            # Wilcoxon 统计量与 Mann-Whitney 统计量是等价的。Wilcoxon 秩和检验主要针对两样本量相同的情况，而 Mann-Whitney 秩和检验考虑到了不等样本的情况，算是对 Wilcoxon 秩和检验这一方法的补充。
            # 参考文章https://blog.csdn.net/Raider_zreo/article/details/101673853
            if len(data1) == len(data2):
                # Wilcoxon 秩和检验
                w_statistic, w_pvalue = stats.wilcoxon(data1, data2, alternative='two-sided')
            else:
                #  Mann-Whitney秩和检验
                w_statistic,w_pvalue = stats.mannwhitneyu(data1, data2, alternative='two-sided')
            return w_pvalue
    except Exception as e:
        logger.exception(f"Exception Logged{str(e)}; data1:{data1},data2:{data2}")
        return None


def sub_dfp_analysis_correlation(data1,data2):
    ttest_statistic, ttest_pvalue = stats.ttest_rel(data1, data2, nan_policy="omit")
    if isinstance(ttest_pvalue,float):
        return ttest_pvalue
    else:
        return None


def dfp_analysis_correlation(df,groups_dict,correlation_dict,FC_threshold=1.5,E_group=None,p=0.05,already_log2=False,if_p=True):
    # 配对样本检验
    '''
    :param df:
    :param groups_dict: 第一组必须为实验组，第二组为对照组
    FC_threshold是差异倍数阈值
    :return:
    '''
    if len(groups_dict)!=2:
        raise Exception("差异分析暂时只适用于两组之间的差异分析")
    # 先取log2
    if E_group is None:
        E_group = list(groups_dict.keys())[0]
    for i in list(groups_dict.keys()):
        if i!=E_group:
            group2 = i
    group1 = E_group # 第一组的名称
    ngroup_sample =[]
    pgroup_sample =[]
    for value in correlation_dict.values():
        ngroup_sample.append(value["ngroup"])
        pgroup_sample.append(value["pgroup"])
    if (df < 0).values.any():
        already_log2=True
    if not already_log2:
        df1 = df.applymap(lambda x: np.log2(x))
        pvalue = df1.apply(lambda row: sub_dfp_analysis_correlation(row[pgroup_sample], row[ngroup_sample]), axis=1)
        FC = df.apply(lambda row: row[pgroup_sample].mean() / row[ngroup_sample].mean(), axis=1)
        log2FC = df.apply(lambda row: np.log2(row[pgroup_sample].mean() / row[ngroup_sample].mean()),
                          axis=1)
        group1_mean = df.apply(lambda row: row[pgroup_sample].mean(), axis=1)
        group2_mean = df.apply(lambda row: row[ngroup_sample].mean(), axis=1)
    else:
        # 已经取了log2
        pvalue = df.apply(lambda row: sub_dfp_analysis_correlation(row[pgroup_sample], row[ngroup_sample]), axis=1)
        # from scipy.special import exp10
        # df1 = df.applymap(lambda x: exp10(x))
        df1 = df.applymap(lambda x: np.exp2(x))
        FC = df1.apply(lambda row: row[pgroup_sample].mean() / row[ngroup_sample].mean(), axis=1)
        log2FC = df1.apply(lambda row: np.log2(row[pgroup_sample].mean() / row[ngroup_sample].mean()),
                          axis=1)
        group1_mean = df1.apply(lambda row: row[pgroup_sample].mean(), axis=1)
        group2_mean = df1.apply(lambda row: row[ngroup_sample].mean(), axis=1)
    from statsmodels.stats.multitest import fdrcorrection
    p2 = pvalue.dropna()
    rejected,fdr = fdrcorrection(p2)
    a = pd.DataFrame({"fdr": fdr}, index=p2.index)
    b = pd.DataFrame({"fdr": a["fdr"]}, index=pvalue.index)
    result_df = pd.DataFrame({f"{group1}_mean":group1_mean,f"{group2}_mean":group2_mean,"Pvalue":pvalue,"fdr":b["fdr"],"log2FC":log2FC,"FoldChange(FC)":FC},index=df1.index)

    def get_dfp(p_value,fc):
        if p_value<p and fc>=FC_threshold:
            return "up-regulated"
        elif p_value<p and fc<=1/FC_threshold:
            return "down-regulated"
        return "none-significant"

    if not if_p:
        result_df['DEP'] = result_df.apply(lambda row: get_dfp(row['fdr'], row['FoldChange(FC)']), axis=1)
    else:
        result_df['DEP'] = result_df.apply(lambda row: get_dfp(row['Pvalue'], row['FoldChange(FC)']), axis=1)
    return result_df


def dfp_analysis(df,groups_dict,FC_threshold=1.5,E_group=None,p=0.05,already_log2=False,if_p=True):
    '''
    :param df:
    :param groups_dict: 第一组必须为实验组，第二组为对照组
    FC_threshold是差异倍数阈值
    :return:
    '''
    if len(groups_dict)!=2:
        raise Exception("差异分析暂时只适用于两组之间的差异分析")
    # 先取log2
    if E_group is None:
        E_group = list(groups_dict.keys())[0]
    for i in list(groups_dict.keys()):
        if i!=E_group:
            group2 = i
    group1 = E_group # 第一组的名称
    if (df < 0).values.any():
        already_log2=True
    if not already_log2:
        df1 = df.applymap(lambda x: np.log2(x))
        pvalue = df1.apply(lambda row: sub_dfp_analysis(row[groups_dict[group1]], row[groups_dict[group2]]), axis=1)
        FC = df.apply(lambda row: row[groups_dict[group1]].mean() / row[groups_dict[group2]].mean(), axis=1)
        log2FC = df.apply(lambda row: np.log2(row[groups_dict[group1]].mean() / row[groups_dict[group2]].mean()),
                          axis=1)
        group1_mean = df.apply(lambda row: row[groups_dict[group1]].mean(), axis=1)
        group2_mean = df.apply(lambda row: row[groups_dict[group2]].mean(), axis=1)
    else:
        # 已经取了log2
        pvalue = df.apply(lambda row: sub_dfp_analysis(row[groups_dict[group1]], row[groups_dict[group2]]), axis=1)
        # from scipy.special import exp10
        # df1 = df.applymap(lambda x: exp10(x))
        df1 = df.applymap(lambda x: np.exp2(x))
        FC = df1.apply(lambda row: row[groups_dict[group1]].mean() / row[groups_dict[group2]].mean(), axis=1)
        log2FC = df1.apply(lambda row: np.log2(row[groups_dict[group1]].mean() / row[groups_dict[group2]].mean()),
                          axis=1)
        group1_mean = df1.apply(lambda row: row[groups_dict[group1]].mean(), axis=1)
        group2_mean = df1.apply(lambda row: row[groups_dict[group2]].mean(), axis=1)
    from statsmodels.stats.multitest import fdrcorrection
    rejected,fdr = fdrcorrection(pvalue)
    result_df = pd.DataFrame({f"{group1}_mean":group1_mean,f"{group2}_mean":group2_mean,"Pvalue":pvalue,"fdr":fdr,"log2FC":log2FC,"FoldChange(FC)":FC},index=df1.index)

    def get_dfp(p_value,fc):
        if p_value<p and fc>=FC_threshold:
            return "up-regulated"
        elif p_value<p and fc<=1/FC_threshold:
            return "down-regulated"
        return "none-significant"

    if not if_p:
        result_df['DEP'] = result_df.apply(lambda row: get_dfp(row['fdr'], row['FoldChange(FC)']), axis=1)
    else:
        result_df['DEP'] = result_df.apply(lambda row: get_dfp(row['Pvalue'], row['FoldChange(FC)']), axis=1)
    return result_df


def sub_dfp_analysis_three(row,groups_dict):
    '''
    :param row:
    :param groups:
    :return:
    '''
    group_name_list = list(groups_dict.keys())
    group_name1 = group_name_list[0]
    group_name2 = group_name_list[1]
    group_name3 = group_name_list[2]
    data1 = row[groups_dict[group_name1]]
    data2 = row[groups_dict[group_name2]]
    data3 = row[groups_dict[group_name3]]
    from scipy import stats
    # 先进行正态分布检验和方差齐性检验
    isnormal_statistic, isnormal_pvalue = stats.shapiro(row)
    levene_statistic, levene_pvalue = stats.levene(data1,data2,data3)
    if isnormal_pvalue>0.05 and levene_pvalue>0.05:
        # 进行方差分析
        f,p = stats.f_oneway(data1,data2,data3)
    else:
        # kruskal-wallis秩和检验
        f,p = stats.kruskal(data1,data2,data3)
    if p<0.05:
        # 认为各组之间平均数不完全相等，进行两两(采用t检验)统计学分析
        # group1—group2
        s12, p12 = stats.ttest_ind(data1, data2)
        # group2—group3
        s23, p23 = stats.ttest_ind(data2, data3)
        # group1—group3
        s13, p13 = stats.ttest_ind(data1, data3)
        # 对p值进行FDR校正
        from statsmodels.stats.multitest import fdrcorrection
        rejected,pvalue_corrected = fdrcorrection([p12,p13,p23])
        q12,q13,q23 = pvalue_corrected[0], pvalue_corrected[1], pvalue_corrected[2]
    else:
        q12, q13, q23 = None,None,None
    return p,q12,q13, q23


def dfp_analysis_three(df,groups_dict,FC_threshold=1.5):
    '''
    单因素三水平差异分析
    :param df:
    :param groups:{"A":[],"B":[]}
    :param FC_threshold:
    :return:
    '''
    if len(groups_dict) != 3:
        raise Exception("适用于单因素三水平差异分析")
    # 先取log2
    df1 = df.applymap(lambda x: np.log2(x))
    group_name_list = list(groups_dict.keys())
    group_name1 = group_name_list[0]
    group_name2 = group_name_list[1]
    group_name3 = group_name_list[2]
    # group1:均值； group1-group2-group3：p值； group1-group2：q值，FoldChange(FC)，log2FC
    p, q12, q13, q23 = zip(*df1.apply(lambda row: sub_dfp_analysis_three(row,groups_dict), axis=1))
    group1_mean = df.apply(lambda row: row[groups_dict[group_name1]].mean(), axis=1)
    group2_mean = df.apply(lambda row: row[groups_dict[group_name2]].mean(), axis=1)
    group3_mean = df.apply(lambda row: row[groups_dict[group_name3]].mean(), axis=1)
    group12_fc = df.apply(lambda row: row[groups_dict[group_name1]].mean()/row[groups_dict[group_name2]].mean(), axis=1)
    group13_fc = df.apply(lambda row: row[groups_dict[group_name1]].mean()/row[groups_dict[group_name3]].mean(), axis=1)
    group23_fc = df.apply(lambda row: row[groups_dict[group_name2]].mean()/row[groups_dict[group_name3]].mean(), axis=1)
    group12_log2fc = df1.apply(lambda row: row[groups_dict[group_name1]].mean()-row[groups_dict[group_name2]].mean(), axis=1)
    group13_log2fc = df1.apply(lambda row: row[groups_dict[group_name1]].mean()-row[groups_dict[group_name3]].mean(), axis=1)
    group23_log2fc = df1.apply(lambda row: row[groups_dict[group_name2]].mean()-row[groups_dict[group_name3]].mean(), axis=1)
    result_df = pd.DataFrame({f"{group_name1}_mean":group1_mean,
                              f"{group_name2}_mean":group2_mean,
                              f"{group_name3}_mean":group3_mean,
                              f"{group_name1}-{group_name2}-{group_name3}-Pvalue":p,
                              f"{group_name1}-{group_name2}-Q":q12,
                              f"{group_name1}-{group_name2}-FoldChange(FC)":group12_fc,
                              f"{group_name1}-{group_name2}-log2FC":group12_log2fc,
                              f"{group_name1}-{group_name3}-Q":q13,
                              f"{group_name1}-{group_name3}-FoldChange(FC)":group13_fc,
                              f"{group_name1}-{group_name3}-log2FC":group13_log2fc,
                              f"{group_name2}-{group_name3}-Q":q23,
                              f"{group_name2}-{group_name3}-FoldChange(FC)":group23_fc,
                              f"{group_name2}-{group_name3}-log2FC":group23_log2fc},index=df1.index)
    return result_df


