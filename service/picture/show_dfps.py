import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config.picture_config import legend_font_size,title_font_size,label_font_size,ticks_font_size,heatmap_cmaps,small_figsize_size,three_color_list
import matplotlib as mpl
import seaborn as sns
from service.difference_analysis.UtilService import get_tmp_dir
from config.global_config import save_png
import os

plt.rcParams.update({'font.size': legend_font_size,'legend.fontsize': 16})
plt.rc('font',family='Times New Roman')


def dfps_scatterplot(result,pdf,title=None,FC_threshold=1.5,pvalue_colname="Pvalue",log2fc_colname = "log2FC",dfp_colname="DEP",p_value=0.05,dir_path=None):
    '''
    画差异蛋白的火山图
    :param result:
    :param title:
    :return:
    '''
    pdf.attach_note("Volcano plots :\nVolcano plots can be used to show the distribution of differences in gene expression levels between two groups of samples.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=small_figsize_size)
    result['log(pvalue)'] = -np.log10(result[pvalue_colname])
    ax = sns.scatterplot(x=log2fc_colname, y="log(pvalue)",
                         hue=dfp_colname, s=50,
                         hue_order=('up-regulated', 'none-significant', 'down-regulated'),
                         palette=("#E41A1C", "#737373", "blue"),
                         data=result)
    if pvalue_colname=="fdr":
        ax.set_ylabel('-$\mathregular{log_{10}}$ p.adjust', fontsize=label_font_size)
    else:
        ax.set_ylabel('-$\mathregular{log_{10}}$ pValue', fontsize=label_font_size)
    ax.set_xlabel('$\mathregular{log_2}$ FoldChange', fontsize=label_font_size)
    plt.xticks(fontsize=ticks_font_size)
    plt.yticks(fontsize=ticks_font_size)

    plt.axvline(-np.log2(FC_threshold),color="black", linestyle='dashed', linewidth=1.5)
    plt.axvline(np.log2(FC_threshold),color="black", linestyle='dashed', linewidth=1.5)
    plt.axhline(-np.log10(p_value), color="black",linestyle='dashed', linewidth=1.5)
    if title:
        plt.title(title,size=title_font_size,fontweight='bold')
    # plt.tight_layout()
    plt.legend(bbox_to_anchor=(1.05, 0.5), loc=6, borderaxespad=0,handletextpad=0.5,markerscale=1,fontsize=legend_font_size)
    plt.subplots_adjust(bottom=0.3,left=0.2,right=0.65,top=0.8)
    pdf.savefig()
    if save_png:
        if dir_path is None:
            dir_path = get_tmp_dir()
        png_path = os.path.join(dir_path, "volcano_plot.png")
        plt.savefig(png_path, dpi=300)
    plt.close()


def dfps_heatmap(df,groups,pdf,dfp_col_name="DEP",row_cluster=False,title=None,dir_path=None):
    if len(df)>0:
        pdf.attach_note("Heatmap :\nHeatmap can be used to display the expression levels of multiple genes in different samples.", positionRect=[0, 0, 0, 0])
        simples = []
        for group in groups:
            simples.extend(group)
        df1 = df.loc[:, simples].copy()

        # related = df[dfp_col_name]
        # lut = dict(zip(related.unique(), "cmy"))
        # row_colors = related.map(lut)

        col_num = []
        cols = []
        for i in range(len(groups)):
            col_num.extend([i for j in range(len(groups[i]))])
            cols.extend(groups[i])
        col_series = pd.Series(data=col_num,index=cols)
        col_lut = dict(zip(col_series.unique(), three_color_list))
        col_colors = col_series.map(col_lut)
        # 加上col_cluster=False，不对列进行聚类
        sns.set(style=None, font_scale=1.5)
        if row_cluster:
            g = sns.clustermap(df1, col_cluster=False, row_cluster=row_cluster, z_score=0, figsize=(11.7, 8.3),
                           cmap=heatmap_cmaps, col_colors=col_colors)
        else:
            g = sns.clustermap(df1, col_cluster=False, row_cluster=row_cluster, z_score=0, figsize=(11.7, 8.3),
                           cmap=heatmap_cmaps, col_colors=col_colors, cbar_pos=(.09, .25, .03, .4))
        if df1.shape[1]>35:
            plt.xticks([])
        else:
            plt.xticks(fontsize=ticks_font_size+2)
        plt.yticks(fontsize=ticks_font_size+2)
        if title:
            g.fig.suptitle(title, size=title_font_size, fontweight='bold')
            # plt.title(title,size=title_font_size,fontweight='bold')
        # plt.tight_layout()
        pdf.savefig()
        if save_png:
            if dir_path is None:
                dir_path = get_tmp_dir()
            png_path = os.path.join(dir_path, "heatmap_plot.png")
            plt.savefig(png_path, dpi=300)
        plt.close()
        mpl.rc_file_defaults()