import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import numpy as np
import seaborn as sns
import matplotlib as mpl
from config.picture_config import legend_font_size, title_font_size, label_font_size, ticks_font_size, heatmap_cmaps, \
   normal_figsize_size,color_list
from util.Util import adaptive_font_size
from service.difference_analysis.UtilService import get_tmp_dir
from config.global_config import save_png
import os

plt.rcParams.update({'font.size': legend_font_size,'legend.fontsize': 16})
plt.rc('font',family='Times New Roman')


def draw_correlation_heatmap(df1,pdf,rowvar=False,dir_path=None):
    '''
    画各个维度之间的相关性热图，https://blog.csdn.net/weixin_39873741/article/details/112215759
    :param df:
    :param rowvar: rowvar=False代表以列未维度，反之以行为维度
    :return:
    '''
    new_ticks_font_size = adaptive_font_size(df1.shape[1], ticks_font_size,df1.columns.tolist())
    pdf.attach_note("Correlation heatmap between samples.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=(11.7, 8.3))
    # pearson：Pearson相关系数来衡量两个数据集合是否在一条线上面，即针对线性数据的相关系数计算，针对非线性数据便会有误差。
    # kendall：用于反映分类变量相关性的指标，即针对无序序列的相关系数，非正太分布的数据
    # spearman：非线性的，非正太分布的数据的相关系数
    if rowvar:
        df1 = df1.transpose()
    corr_matrix = df1.corr(method ='pearson')
    mask = np.zeros_like(corr_matrix)
    mask[np.triu_indices_from(mask)] = True
    ax0 = plt.gca()
    # sns.heatmap(corr_matrix,xticklabels=1,yticklabels=1,square=True,cmap=sns.cm.rocket_r, annot=True, annot_kws={"size": 25 / np.sqrt(len(corr_matrix))})
    h = sns.heatmap(corr_matrix,square=True,cmap=heatmap_cmaps,ax=ax0, cbar=False,
                annot=True,mask=mask,annot_kws={'size': new_ticks_font_size - 6})
    cb = h.figure.colorbar(h.collections[0])  # 显示colorbar
    cb.ax.tick_params(labelsize=legend_font_size)  # 设置colorbar刻度字体大小。
    plt.xlabel("",fontsize=label_font_size)
    plt.ylabel("",fontsize=label_font_size)
    plt.xticks(rotation=45, fontsize=new_ticks_font_size,ha='right')  # 放大横轴坐标并逆时针旋转45°
    plt.yticks(fontsize=new_ticks_font_size)  # 放大纵轴坐标
    plt.tight_layout()
    pdf.savefig()
    if save_png:
        if dir_path is None:
            dir_path = get_tmp_dir()
        png_path = os.path.join(dir_path,"correlation_heatmap_plot.png")
        plt.savefig(png_path, dpi=300)
    plt.close()


def draw_table(df):
    '''
    画图表
    :param df:
    :return:
    '''
    plt.figure(figsize=(11.7, 8.3))
    row_length = len(df.index)
    col_length = len(df.columns)
    cellColours = [["#e5e5e5" for j in range(col_length)]for i in range(row_length)]
    tab = plt.table(cellText=df.values,
                    colLabels=df.columns,
                    rowLabels=df.index,
                    loc='center',
                    cellLoc='center',
                    cellColours=cellColours,
                    rowColours=["#48cae4" for i in range(row_length)],
                    colColours=["#52b69a" for i in range(col_length)],
                    rowLoc='center')
    tab.scale(1, 2)
    plt.axis('off')
    plt.show()


def draw_venn2(data1,data2,label1,label2,show_intersection_text=False):
    '''
    画二维韦恩图 https://zhuanlan.zhihu.com/p/195541937
    :param show_intersection_text: 是否展示交集的具体内容,但是交集部分过多也不会展示
    :param data1:
    :param data2:
    :param label1:
    :param label2:
    :return:
    '''
    plt.figure(figsize=(11.7, 8.3))
    set1 = set(data1)
    set2 = set(data2)
    g = venn2([set1, set2], set_labels=(label1, label2))
    for t in g.set_labels:
        if t:
            t.set_fontsize(22)

    for t in g.subset_labels:
        if t:
            t.set_fontsize(20)
    set12 = set1.intersection(set2)
    if len(set12)<=10 and show_intersection_text:
        plt.annotate(set(set12),
                     color='black',
                     xy=g.get_label_by_id('11').get_position() + np.array([0, 0.05]),
                     xytext=(20, 80),
                     ha='center', textcoords='offset points',
                     bbox=dict(boxstyle='round,pad=0.5', fc='grey', alpha=0.6),
                     arrowprops=dict(arrowstyle='-|>', connectionstyle='arc3,rad=-0.5', color='black'),
                     fontsize=15
                     )
    plt.show()


def draw_barplot(data_dict,title=None):
    fig, ax = plt.subplots()
    ax.bar(x=list(data_dict.keys()), height=list(data_dict.values()),align="center",width=0.6,color=['r','g','b', 'c', 'm', 'y'], edgecolor="black",linewidth=1.0)
    if title:
        ax.set_title(title,fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    xticks = ax.get_xticks()
    for i in range(len(data_dict)):
        xy = (xticks[i], list(data_dict.values())[i] * 1.001)
        s = str(list(data_dict.values())[i])
        ax.annotate(
            s,  # 要添加的文本
            xy=xy,  # 将文本添加到哪个位置
            fontsize=15,  # 标签大小
            ha="center",  # 水平对齐
            va="baseline"  # 垂直对齐
        )
    plt.show()


def draw_pie(data_dict,title=None):
    labels = list(data_dict.keys())
    quants = list(data_dict.values())
    # make a square figure
    plt.figure(1, figsize=(6,6))
    # For China, make the piece explode a bit
    expl = []
    for i in range(len(labels)):
        if i==0:
            expl.append(0.05)
        else:
            expl.append(0)
    # Colors used. Recycle if not enough.
    colors  = ["blue","red","coral","green","yellow","orange"]  #设置颜色（循环显示）
    # Pie Plot
    # autopct: format of "percent" string;百分数格式
    patches, l_text, p_text = plt.pie(quants, explode=expl, colors=colors, labels=labels, autopct='%1.1f%%',pctdistance=0.5, shadow=True)
    if title:
        plt.title(title, bbox={'facecolor':'0.8', 'pad':5},fontweight='bold')
    for t in l_text:
        t.set_size(20)
    for t in p_text:
        t.set_size(20)
    plt.show()
    plt.savefig("pie.jpg")
    plt.close()


def draw_line_chart(df,title,pdf,marker='o',legend=True):
    new_ticks_font_size = adaptive_font_size(df.shape[1], ticks_font_size,df.columns.tolist())
    plt.rcParams.update({'font.size': legend_font_size, 'legend.fontsize': 16})
    plt.figure(figsize=normal_figsize_size)
    x= df.columns.to_list()
    for index in df.index:
        y = df.loc[index].to_list()
        plt.plot(x, y, marker=marker, markersize=5)
    if legend:
        plt.legend(df.index.to_list(), bbox_to_anchor=(1.05, 0.5), loc=6, borderaxespad=0,title="Class",
                   handletextpad=0.5, fontsize=legend_font_size)
    plt.title(title, size=title_font_size, fontweight='bold')
    if len(df.columns)>60:
        plt.xticks([])
    else:
        plt.xticks(rotation=45,fontsize=new_ticks_font_size,ha='right')  # 放大横轴坐标并逆时针旋转45°
    plt.yticks(fontsize=new_ticks_font_size)  # 放大纵轴坐标
    plt.xlabel("Samples", fontsize=label_font_size)
    plt.ylabel("$\mathregular{log_2}$ Intensity", fontsize=label_font_size)
    # plt.tight_layout()
    plt.subplots_adjust(bottom=0.2, left=0.15, right=0.75, top=0.85)
    pdf.savefig()
    plt.close()


def draw_heatmap(df,title,pdf,groups):
    pdf.attach_note("Heatmap :\nHeatmap can be used to display the expression levels of multiple genes in different samples and different classes.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=normal_figsize_size)

    df.sort_values(by="class_label", inplace=True, ascending=True)
    df = df[df.columns.difference(['class_label'])].T

    if len(df)>0:
        pdf.attach_note("Heatmap :\nHeatmap can be used to display the expression levels of multiple genes in different samples.", positionRect=[0, 0, 0, 0])
        simples = []
        for group in groups:
            simples.extend(group)
        df1 = df.loc[:, simples].copy()

        col_num = []
        cols = []
        for i in range(len(groups)):
            col_num.extend([i for j in range(len(groups[i]))])
            cols.extend(groups[i])
        import pandas as pd
        col_series = pd.Series(data=col_num,index=cols)
        col_lut = dict(zip(col_series.unique(), color_list))
        col_colors = col_series.map(col_lut)

        sns.set(style=None, font_scale=1.5)
        g = sns.clustermap(df1, col_cluster=False, row_cluster=False, z_score=0, figsize=(11.7, 8.3),
                       cmap=heatmap_cmaps,col_colors=col_colors, cbar_pos=(.09, .25, .03, .4))
        if df1.shape[1]>35:
            plt.xticks([])
        else:
            plt.xticks(fontsize=ticks_font_size+2)
        plt.yticks(fontsize=ticks_font_size+2)
        if title:
            g.fig.suptitle(title, size=title_font_size, fontweight='bold')
        pdf.savefig()
        plt.close()
        mpl.rc_file_defaults()


