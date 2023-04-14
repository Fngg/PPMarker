# 展示数据缺失情况
import missingno as msno # 展示缺失值情况的图表
import matplotlib.pyplot as plt
from util.ColorHadler import Hex_to_RGB_float_tuple,RGB_tuple_RGB_float_tuple
from config.picture_config import legend_font_size,label_font_size,ticks_font_size,heatmap_cmaps
from config.global_config import save_png
from util.Util import adaptive_font_size
from util.Logger import logger
from service.difference_analysis.UtilService import get_tmp_dir
import os

plt.rcParams.update({'font.size': legend_font_size,'legend.fontsize': 16})
plt.rc('font',family='Times New Roman')


def draw_miss(df,pdf,color = (0.01, 0.24, 0.54),dir_path=None):
    '''
    展示数据缺失值情况的图表
    :param df:
    :return:
    '''
    new_ticks_font_size= adaptive_font_size(df.shape[1],ticks_font_size,df.columns.tolist())
    logger.debug("new_ticks_font_size:"+str(new_ticks_font_size))
    if isinstance(color,str):
        color = Hex_to_RGB_float_tuple(color)
    if isinstance(color,tuple) and isinstance(color[0],int):
        color = RGB_tuple_RGB_float_tuple(color)
    pdf.attach_note("Matrix plot:\nThe Matrix plot is a data-dense display which lets you quickly visually pick out patterns in data completion.The sparkline at right summarizes the general shape of the data completeness and points out the rows with the maximum and minimum nullity in the dataset.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=(11.7, 8.3))
    msno.matrix(df,color=color,figsize=(11.7, 8.3))
    # plt.subplots_adjust(top=0.72,bottom=0.08)
    plt.yticks(fontsize=new_ticks_font_size)
    plt.xticks(fontsize=new_ticks_font_size)
    pdf.savefig()
    if save_png:
        if dir_path is None:
            dir_path = get_tmp_dir()
        png_path = os.path.join(dir_path,"miss_matrix_plot.png")
        plt.savefig(png_path, dpi=300)
    plt.close()

    pdf.attach_note("Bar plot:\nYou can see the missing values in each variable with the help of each bar.", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=(11.7, 8.3))
    msno.bar(df,color=color,figsize=(11.7, 8.3),fontsize=new_ticks_font_size-2)
    # plt.subplots_adjust(top=0.9,bottom=0.2)
    plt.yticks(fontsize=new_ticks_font_size)
    plt.xticks(fontsize=new_ticks_font_size)
    # plt.xlabel("simples",fontsize=label_font_size)
    plt.tight_layout()
    pdf.savefig()
    if save_png:
        if dir_path is None:
            dir_path = get_tmp_dir()
        png_path = os.path.join(dir_path,"miss_bar_plot.png")
        plt.savefig(png_path, dpi=300)
    plt.close()
    if df.isnull().any().any():
        # 当有缺失值时需要画热图
        pdf.attach_note("Heatmap:\nThe correlation heatmap measures nullity correlation: how strongly the presence or absence of one variable affects the presence of another.", positionRect=[0, 0, 0, 0])
        plt.figure(figsize=(11.7, 8.3))
        # logger.debug("热力图:表示两个特征之间的缺失相关性，即一个变量的存在或不存在如何强烈影响的另一个的存在。如果x和y的热度值是1，则代表当x缺失时，y也百分之百缺失。如果x和y的热度相关性为-1，说明x缺失的值，那么y没有缺失；而x没有缺失时，y为缺失。")
        h = msno.heatmap(df,figsize=(11.7, 8.3),fontsize=new_ticks_font_size-4,cmap=heatmap_cmaps,cbar=False)
        cb = h.figure.colorbar(h.collections[0])  # 显示colorbar
        cb.ax.tick_params(labelsize=legend_font_size)  # 设置colorbar刻度字体大小。
        # plt.subplots_adjust(top=0.9,bottom=0.2,left=0.2,right=0.9)
        plt.yticks(fontsize=new_ticks_font_size)
        plt.xticks(fontsize=new_ticks_font_size)
        plt.xlabel("simples",fontsize=label_font_size)
        plt.ylabel("simples",fontsize=label_font_size)
        plt.tight_layout()
        pdf.savefig()
        if save_png:
            if dir_path is None:
                dir_path = get_tmp_dir()
            png_path = os.path.join(dir_path, "miss_heatmap_plot.png")
            plt.savefig(png_path, dpi=300)
        plt.close()
