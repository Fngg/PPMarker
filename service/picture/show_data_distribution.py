# 展示数据密度与分布的图表
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from config.picture_config import legend_font_size,title_font_size,label_font_size,ticks_font_size,normal_figsize_size,big_figsize_size,small_figsize_size,three_color_list,color_list
from service.difference_analysis.UtilService import get_color_list
from util.Util import adaptive_font_size
from service.difference_analysis.UtilService import get_tmp_dir
from config.global_config import save_png
import os

plt.rcParams.update({'font.size': legend_font_size,'legend.fontsize': 16})
plt.rc('font',family='Times New Roman')


def draw_boxplot(df1, pdf,groups_dict=None, title=None, log2=True,dir_path=None):
    '''
    箱型图，箱线图表示每个样本的分位数数值大小及数据分布形态，一致性好的数据在 箱线图中应是均一的。
    :param df1: 列的顺序有讲究
    :param pdf:
    :param groups_dict: {"A":[,,,],"B":[,,,]}
    :param title: 标题
    log2:是否需要log2处理
    :return:
    '''
    new_ticks_font_size = adaptive_font_size(df1.shape[1], ticks_font_size,df1.columns.tolist())
    if log2:
        # 当dataframe中最大值和最小值相差的范围在20以内时不需要进行log2处理l;或者有负值
        if (df1.max(skipna=True).max() <100 )or (df1 < 0).values.any():
            log2=False
    # 取对数处理
    if log2:
        df1 = df1.applymap(lambda x: np.log2(x))
    pdf.attach_note("Boxplot:\nThe boxplot represents the quantile value size and data distribution pattern of each sample, and the data with good consistency should be uniform in the boxplot.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=normal_figsize_size)
    color_list,simples = get_color_list(groups_dict,three_color_list) # 设置每个箱体的颜色
    ax = sns.boxplot(data=df1[simples],
                     palette=color_list
                     )
    if len(df1.columns)>60:
        plt.xticks([])
    else:
        plt.xticks(rotation=45,fontsize=new_ticks_font_size,ha='right')  # 放大横轴坐标并逆时针旋转45°
    plt.yticks(fontsize=new_ticks_font_size)  # 放大纵轴坐标
    if log2:
        plt.ylabel("$\mathregular{log_2}$ Intensity", fontsize=label_font_size)
    else:
        plt.ylabel("Intensity", fontsize=label_font_size)
    # Tweak spacing to prevent clipping of tick-labels
    plt.xlabel("Simples", fontsize=label_font_size)
    plt.subplots_adjust(bottom=0.2,left=0.2,right=0.85,top=0.85)
    if title:
        plt.title(title, fontsize=title_font_size,fontweight='bold')
    pdf.savefig()
    if save_png:
        if dir_path is None:
            dir_path = get_tmp_dir()
        png_path = os.path.join(dir_path,"boxplot_plot.png")
        if title:
            if "filtering" in title:
                title = "filtering"
            png_path = os.path.join(dir_path, title+"_boxplot_plot.png")
        plt.savefig(png_path, dpi=300)
    plt.close()


def draw_density(df,pdf, title=None, log2=True):
    '''
    密度图来展示，密度图能直观体现数据分布的正偏态、峰度、均值等信息
    :param df:
    :param title: 标题
    :return:
    '''
    # 取log2对数处理
    if log2:

        df1 = df.applymap(lambda x: np.log2(x))
    else:
        df1 = df
    pdf.attach_note("密度图能直观体现数据分布的正偏态、峰度、均值等信息", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=normal_figsize_size)
    df1.plot.density(linewidth=4)
    if log2:
        plt.ylabel("Log2 Intensity", fontsize=label_font_size)
    else:
        plt.ylabel("Intensity", fontsize=label_font_size)
    plt.xlabel("Log2 Intensity", fontsize=label_font_size)
    if title:
        plt.title(title, fontsize=title_font_size,fontweight='bold')
    plt.tight_layout()
    pdf.savefig()
    plt.close()