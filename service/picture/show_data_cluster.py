# 展示数据的聚类分析，看看
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from operator import itemgetter
from config.picture_config import legend_font_size,title_font_size,label_font_size,ticks_font_size,normal_figsize_size,three_color_list,small_figsize_size,\
    pca_dot_size
from service.difference_analysis.UtilService import group_dict_to_simple_dict
from util.Util import adaptive_font_size
from service.difference_analysis.UtilService import get_tmp_dir
from config.global_config import save_png
import os


plt.rcParams.update({'font.size': legend_font_size,'legend.fontsize': 16})
plt.rc('font',family='Times New Roman')


def mscatter(x, y, ax=None, m=None, **kw):
    import matplotlib.markers as mmarkers
    if not ax: ax = plt.gca()
    sc = ax.scatter(x, y, **kw)
    if (m is not None) and (len(m) == len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc


def draw_pca_cluster(df,groups_dict,title,pdf,is_annotate=False,dir_path=None):
    '''
    is_annotate 是否对PCA上的每个点进行文字标注
    pca 95%的置信区间 https://stackoverflow.com/questions/46732075/python-pca-plot-using-hotellings-t2-for-a-confidence-interval
    '''
    from sklearn.decomposition import PCA
    pdf.attach_note("PCA cluster diagram", positionRect=[0, 0, 0, 0])
    plt.figure(figsize=normal_figsize_size)
    df = df.dropna()
    if len(df)>=2:
        df_T = df.transpose()
        # 对蛋白进行标准差标准化
        df_T_scale = StandardScaler().fit_transform(df_T)
        # 获取分组标签
        y_dict = {}
        all_markers =['o',"^","s","v","+"]
        markers_dict = {}
        keys = list(groups_dict.keys())
        for j in range(len(keys)):
            for k in groups_dict[keys[j]]:
                y_dict[k] = j
                markers_dict[k] = all_markers[j]
        y = list(itemgetter(*list(df_T.index))(y_dict))
        markers = list(itemgetter(*list(df_T.index))(markers_dict))
        model = PCA(n_components=2)
        pca = model.fit_transform(df_T_scale)
        # ratio 主成分方差贡献率
        ratio = model.explained_variance_ratio_
        scatter = plt.scatter(pca[:, 0], pca[:, 1], c=y,s=pca_dot_size)
        # scatter = mscatter(pca[:, 0], pca[:, 1], c=y,s=pca_dot_size,m=markers)
        if is_annotate:
            for i in range(len(pca[:, 0])):
                plt.annotate(list(df_T.index)[i], xy=(pca[i, 0], pca[i, 1]), xytext=(pca[i, 0] + 0.06, pca[i, 1] + 0.06))  # 这里xy是需要标记的坐标，xytext是对应的标签坐标
        legend_labels = []
        for key in keys:
            legend_labels.append("$\\mathdefault{"+key+"}$")
        plt.legend(scatter.legend_elements()[0],legend_labels,bbox_to_anchor=(1.05, 0.5), loc=6, borderaxespad=0,handletextpad=0.5,fontsize=legend_font_size)
        plt.title(title, size=title_font_size,fontweight='bold')
        plt.yticks(fontsize=ticks_font_size)
        plt.xticks(fontsize=ticks_font_size)
        plt.xlabel(f"PC1({round(ratio[0]*100,2)}%)",fontsize=label_font_size)
        plt.ylabel(f"PC2({round(ratio[1]*100,2)}%)",fontsize=label_font_size)
        # plt.tight_layout()
        plt.subplots_adjust(bottom=0.2,left=0.15,right=0.75,top=0.85)
        pdf.savefig()
        if save_png:
            if dir_path is None:
                dir_path = get_tmp_dir()
            png_path = os.path.join(dir_path, "pca_cluster_plot.png")
            if title:
                if "filtering" in title:
                    title = "filtering"
                png_path = os.path.join(dir_path,title+"_pca_cluster_plot.png")
            plt.savefig(png_path, dpi=300)
        plt.close()


def draw_tree_cluster(df,pdf,groups_dict,title=None,dir_path=None):
    '''
    画树状聚类图
    df：行为蛋白，列为样本
    title： 标题
    group_dict：传入group_dict，画树状图的时候将leaf_label_func
    '''
    import scipy.cluster.hierarchy as sch
    plt.figure(figsize=(11.7, 8.3))
    pdf.attach_note("Dendrogram:\nClustering samples into distinct classes using unsupervised clustering learning.", positionRect=[0, 0, 0, 0])

    df1 = df.dropna()
    new_ticks_font_size = adaptive_font_size(df1.shape[1], ticks_font_size,df1.columns.tolist())
    if len(df)!=0:
        df_T1 = df1.transpose()
        # 对列（蛋白）进行标准化
        df_T = StandardScaler().fit_transform(df_T1)
        # 生成点与点之间的距离矩阵,这里用的欧氏距离:
        disMat = sch.distance.pdist(df_T, 'euclidean')
        # 进行层次聚类:
        Z = sch.linkage(disMat, method='average')
        # 将层级聚类结果以树状图表示出来
        sch.dendrogram(Z, labels=df.columns)
        simple_dict = group_dict_to_simple_dict(groups_dict)
        # 设置标签的颜色分组
        ax = plt.gca()
        # 获得y轴坐标标签
        xlbls = ax.get_xmajorticklabels()
        num = -1
        for lbl in xlbls:
            num += 1
            val = simple_dict[lbl.get_text()]
            # 设置颜色
            lbl.set_color(three_color_list[val])

        if title:
            plt.title(title,fontsize=title_font_size,fontweight='bold')
        plt.xticks(rotation=45, fontsize=new_ticks_font_size,ha='right')  # 放大横轴坐标并逆时针旋转45°
        plt.yticks(fontsize=new_ticks_font_size)  # 放大纵轴坐标
        # plt.tight_layout()
        plt.subplots_adjust(bottom=0.2,left=0.2,right=0.85,top=0.85)
        pdf.savefig()
        if save_png:
            if dir_path is None:
                dir_path = get_tmp_dir()
            png_path = os.path.join(dir_path, "tree_cluster_plot.png")
            if title:
                png_path = os.path.join(dir_path,title+"_tree_cluster_plot.png")
            plt.savefig(png_path, dpi=300)
        plt.close()