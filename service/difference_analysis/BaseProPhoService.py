import numpy as np


def pho_dfp_base_pro(all,complement_expression_df,pro_dfp_df,pro_supplementary_df,FC_threshold,p=0.05,pvalue_colname="Pvalue"):
    '''
    用蛋白质组的差异结果对磷酸化组的差异结果进行校正
    '''
    pho_index_name = complement_expression_df.columns[0]
    pro_index_name = pro_supplementary_df.columns[0]
    pho_df = all.merge(complement_expression_df[pho_index_name], how='left', left_index=True, right_index=True)
    pro_df = pro_dfp_df.merge(pro_supplementary_df[pro_index_name], how='left', left_index=True, right_index=True)

    def sub_fuc(name,simple):
        if name not in list(pro_df[pro_index_name]):
            return None
        else:
            return pro_df.loc[pro_df[pro_index_name]==name,simple].iloc[0]
    pro_pvalue_colname="pro_"+pvalue_colname
    pho_df[pro_pvalue_colname] = pho_df.apply(lambda row:sub_fuc(row[pho_index_name],pvalue_colname),axis=1)
    pho_df["pro_FoldChange(FC)"] = pho_df.apply(lambda row:sub_fuc(row[pho_index_name],"FoldChange(FC)"),axis=1)
    pho_df["pro_DEP"] = pho_df.apply(lambda row:sub_fuc(row[pho_index_name],"DEP"),axis=1)

    def sub_fuc2(row):
        # nan值，通常是个浮点型数据， 有时候很难识别出nan值。nan值，通常是个浮点型数据， 有时候很难识别出nan值。
        if row["pro_FoldChange(FC)"] is not None:
            return row["FoldChange(FC)"]/row["pro_FoldChange(FC)"]
        else:
            return row["FoldChange(FC)"]

    pho_df["finally_FoldChange(FC)"] = pho_df.apply(lambda row: sub_fuc2(row),axis=1)
    pho_df["finally_log2FC"] = pho_df.apply(lambda row: np.log2(row["finally_FoldChange(FC)"]), axis=1)

    def get_dfp(p_value,fc):
        if p_value<p and fc>=FC_threshold:
            return "up-regulated"
        elif p_value<p and fc<=1/FC_threshold:
            return "down-regulated"
        return "none-significant"

    pho_df['finally_DEP'] = pho_df.apply(lambda row: get_dfp(row[pvalue_colname], row["finally_FoldChange(FC)"]), axis=1)
    return pho_df


