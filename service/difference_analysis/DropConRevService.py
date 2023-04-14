def drop_CON_REV(df):
    '''
    删除污染和反库蛋白 删除 Reverse / Potential contaminant 列中值为”+“的蛋白
    '''
    reverse_col_name = "Reverse"
    contaminant_col_name = "contaminant"
    for col_name in df.columns:
        if reverse_col_name.lower() in col_name.lower():
            reverse_col_name = col_name
        if contaminant_col_name.lower() in col_name.lower():
            contaminant_col_name = col_name
    if reverse_col_name in df.columns and contaminant_col_name in df.columns:
        result = df.loc[(df[reverse_col_name]!="+")&(df[contaminant_col_name]!="+")]
        describe = f"we remove {df.shape[0]-result.shape[0]} Reverse and Potential contaminant proteins."
        return result,describe
    else:
        return df, "No Reverse and Potential contaminant."