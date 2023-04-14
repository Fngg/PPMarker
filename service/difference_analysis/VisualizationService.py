from service.picture.show_dynamic_html import volcano_plot_html, pca_plot_html
from service.picture.show_miss import draw_miss
from service.picture.show_data_distribution import draw_boxplot
from service.picture.show_data_cluster import draw_tree_cluster,draw_pca_cluster
from service.picture.basic import draw_correlation_heatmap
from service.picture.show_dfps import dfps_scatterplot,dfps_heatmap
from matplotlib.backends.backend_pdf import PdfPages
from service.difference_analysis.MissingService import base_missing_filing
from config.global_config import software_name,Quality_Assessment_dirname,Normalization_and_Filtering_dirname,Difference_Analysis_dirname,Enrichment_Analysis_dirname
import os,datetime
import pandas as pd

# import matplotlib.pyplot as plt
#
# plt.rcParams.update({'figure.autolayout': True})

def judge_dataframe_empty(df):
    if df.empty:
        return True
    else:
        return None


def data_assesment(df,result_dir,groups_dict,groups,simples,dirname=Quality_Assessment_dirname):
    if judge_dataframe_empty(df):
        return None
    file_path = os.path.join(result_dir,dirname,"Show_Missing.pdf")
    dir_path = os.path.join(result_dir,dirname)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    pdf = PdfPages(file_path,metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(), 'Title': 'Data Assessment'})
    # 缺失值情况
    draw_miss(df,pdf,dir_path=dir_path)
    draw_correlation_heatmap(df, pdf,dir_path=dir_path)
    draw_boxplot(df[simples],pdf,groups_dict,title="raw",dir_path=dir_path)
    draw_tree_cluster(df,pdf,groups_dict,dir_path=dir_path)
    draw_pca_cluster(df,groups_dict,"PCA of Raw",pdf,dir_path=dir_path)
    PCA_file_path = os.path.join(result_dir, dirname, "PCA.html")
    pca_plot_html(df,PCA_file_path,groups_dict,title="PCA of Raw")
    pdf.close()


def data_norm(ori_df,norm_df,norm_method,result_dir,groups_dict,file_name="Show_Normalization.pdf",dirname=Normalization_and_Filtering_dirname):
    '''
    数据校正前后的箱型图对比
    '''
    if judge_dataframe_empty(ori_df) or judge_dataframe_empty(norm_df):
        return None
    file_path = os.path.join(result_dir,dirname,file_name)
    dir_path = os.path.join(result_dir, dirname)
    pdf = PdfPages(file_path,metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(), 'Title': 'Data Normalization'})
    draw_boxplot(ori_df,pdf,groups_dict,title="raw",dir_path=dir_path)
    draw_boxplot(norm_df,pdf,groups_dict,title=norm_method,dir_path=dir_path)
    pdf.close()


def data_filter(ori_df,filter_df,miss_n,result_dir,groups_dict,dirname=Normalization_and_Filtering_dirname):
    '''
    分组过滤，各组 n ≥ miss_n 留下
    '''
    if judge_dataframe_empty(ori_df) or judge_dataframe_empty(filter_df):
        return None
    file_path = os.path.join(result_dir,dirname,"Show_Filter_Missing_Value.pdf")
    dir_path = os.path.join(result_dir, dirname)
    pdf = PdfPages(file_path,metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(), 'Title': 'Filter Missing Value'})
    draw_boxplot(ori_df,pdf,groups_dict,title="Normalization",dir_path=dir_path)
    draw_boxplot(filter_df,pdf,groups_dict,title="group filtering",dir_path=dir_path)
    draw_pca_cluster(ori_df,groups_dict,"Normalization",pdf,dir_path=dir_path)

    PCA_raw_file_path = os.path.join(result_dir, dirname, "PCA_Normalization.html")
    pca_plot_html(ori_df,PCA_raw_file_path,groups_dict,title="Normalization")

    draw_pca_cluster(filter_df,groups_dict,"group filtering",pdf,dir_path=dir_path)

    PCA_filter_file_path = os.path.join(result_dir, dirname, "PCA_filter.html")
    pca_plot_html(filter_df,PCA_filter_file_path,groups_dict,title="group filtering")

    pdf.close()


def data_imputation(ori_df,imputation_df,imputation_way,result_dir,groups_dict,dirname):
    '''
    分组过滤，各组 n ≥ miss_n 留下
    '''
    if judge_dataframe_empty(ori_df) or judge_dataframe_empty(imputation_df):
        return None
    file_path = os.path.join(result_dir,dirname,"Show_Data_Imputation_Value.pdf")
    dir_path = os.path.join(result_dir, dirname)
    pdf = PdfPages(file_path,metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(), 'Title': 'Data Imputation'})
    draw_boxplot(ori_df,pdf,groups_dict,title="raw",dir_path=dir_path)
    draw_boxplot(imputation_df,pdf,groups_dict,title=imputation_way,dir_path=dir_path)
    draw_pca_cluster(ori_df,groups_dict,"Raw",pdf,dir_path=dir_path)

    PCA_raw_file_path = os.path.join(result_dir, dirname, "PCA_raw.html")
    pca_plot_html(ori_df,PCA_raw_file_path,groups_dict,title="Raw")

    draw_pca_cluster(imputation_df,groups_dict,imputation_way,pdf,dir_path=dir_path)

    PCA_imputation_file_path = os.path.join(result_dir, dirname, "PCA_imputation.html")
    pca_plot_html(imputation_df,PCA_imputation_file_path,groups_dict,title=imputation_way)
    pdf.close()


def data_dfp_analysis(all,FC_threshold,groups,simples,groups_dict,result_dir,dirname=Difference_Analysis_dirname,pvalue_colname="Pvalue",log2fc_colname = "log2FC",dfp_colname="DEP",p_value=0.05):
    '''
    差异分析，可视化展示：火山图，聚类图，热图。
    '''
    if judge_dataframe_empty(all):
        return None
    file_path = os.path.join(result_dir, dirname, "Show_Difference_Analysis_Result.pdf")
    dir_path = os.path.join(result_dir, dirname)
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'Difference Analysis Result'})
    # 差异蛋白火山图
    dfps_scatterplot(all,pdf,FC_threshold=FC_threshold,pvalue_colname=pvalue_colname,log2fc_colname = log2fc_colname,dfp_colname=dfp_colname,p_value=p_value,dir_path=dir_path)
    volcano_html_file_path= os.path.join(result_dir, dirname, "volcano_plot.html")
    volcano_plot_html(all,volcano_html_file_path,FC_threshold=FC_threshold,pvalue_colname=pvalue_colname,log2fc_colname = log2fc_colname,dfp_colname=dfp_colname)
    dfp_index = all.loc[all[dfp_colname] != "none-significant", :].index
    draw_pca_cluster(all.loc[dfp_index,simples],groups_dict,"Differential Proteins",pdf,dir_path=dir_path)

    PCA_file_path = os.path.join(result_dir, dirname, "PCA_based_on_differential_proteins.html")
    pca_plot_html(all.loc[dfp_index,simples],PCA_file_path,groups_dict,title="Differential Proteins")
    # 热图不能忍受缺失值，所以将缺失值以最小值的方式填补
    if all.loc[:, simples].isnull().any().any():
        df1 = base_missing_filing(all.loc[:,simples], groups)
        df2 = pd.concat([df1, all[dfp_colname]], axis=1)
        df3 = df2.loc[dfp_index, :]
    else:
        tmp = simples.copy()
        tmp.append(dfp_colname)
        df3 = all.loc[dfp_index,tmp].copy()
    def sub_fuc(row):
        name = str(row.name)
        if len(name)>25:
            return name.split("_")[-1]
        return name
    df3.index = df3.apply(lambda row: sub_fuc(row), axis=1)
    df3.sort_values(by=dfp_colname, inplace=True, ascending=True)
    dfps_heatmap(df3, groups,pdf,dir_path=dir_path)
    pdf.close()