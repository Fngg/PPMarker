from PyQt5.QtGui import QImage, QPixmap
from graphviz import Digraph
import util.Global as gol
import os


def biomarker_marked_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "biomarker_marked.gv")

    gz = Digraph("biomarker_marked", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)
    gz.node('0', '（当为蛋白质组数据时）删除污染与反库蛋白\n删除 Reverse / Potential contaminant 列中值为”+“的蛋白')
    biomarker_marked_norm = gol.get_value("biomarker_marked_norm")
    gz.node('1', f'数据校正\n{biomarker_marked_norm}-样本间（列）校正/做ratio-蛋白（行）校正')

    biomarker_marked_filter_index = gol.get_value("biomarker_marked_filter_index")
    if biomarker_marked_filter_index == 0:
        biomarker_marked_miss_n = gol.get_value("biomarker_marked_miss_n")
        gz.node('2', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{biomarker_marked_miss_n}过滤掉')
    else:
        biomarker_marked_miss_ratio = gol.get_value("biomarker_marked_miss_ratio")
        gz.node('2', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{biomarker_marked_miss_ratio}%过滤掉')

    biomarker_marked_imputation = gol.get_value("biomarker_marked_imputation")
    gz.node('3', f'缺失值填补\n{biomarker_marked_imputation}')
    biomarker_marked_train_ratio = gol.get_value("biomarker_marked_train_ratio")
    biomarker_marked_test_ratio = gol.get_value("biomarker_marked_test_ratio")
    biomarker_marked_verification_ratio = gol.get_value("biomarker_marked_verification_ratio")
    gz.node('4',
            f'数据集拆分比例\n训练集：{biomarker_marked_train_ratio}，验证集：{biomarker_marked_verification_ratio}，测试集：{biomarker_marked_test_ratio}')
    biomarker_marked_feature_select_index = gol.get_value("biomarker_marked_feature_select_index")
    biomarker_marked_feature_select = gol.get_value("biomarker_marked_feature_select")
    biomarker_marked_max_feature_num = gol.get_value("biomarker_marked_max_feature_num")
    if biomarker_marked_feature_select_index in [0, 1, 2, 3, 4]:
        biomarker_marked_p = gol.get_value("biomarker_marked_p")
        biomarker_marked_fc = gol.get_value("biomarker_marked_fc")
        p_threshold_index = gol.get_value("biomarker_marked_p_threshold_index")
        if p_threshold_index == 0:
            gz.node('5',
                    f'特征筛选-{biomarker_marked_feature_select}\nP ≤ {biomarker_marked_p} and {biomarker_marked_fc}\n筛选后的特征数不多于:{biomarker_marked_max_feature_num}')
        else:
            gz.node('5',
                    f'特征筛选-{biomarker_marked_feature_select}\nFDR ≤ {biomarker_marked_p} and {biomarker_marked_fc}\n筛选后的特征数不多于:{biomarker_marked_max_feature_num}')

    else:
        gz.node('5',
                f'特征筛选-{biomarker_marked_feature_select}\n筛选后的特征数不多于:{biomarker_marked_max_feature_num}')
    biomarker_marked_classifier = gol.get_value("biomarker_marked_classifier")
    gz.node('6', f'分类器算法\n{biomarker_marked_classifier}')
    gz.edges(['01', "12", "23", "34", "45", "56"])
    gz.render(gv_path, format='png', view=False)
    return gv_path + ".png"


def biomarker_label_free_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path,"tmp","biomarker_label_free.gv")

    gz = Digraph("biomarker_label_free", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)
    gz.node('0', '（当为蛋白质组数据时）删除污染与反库蛋白\n删除 Reverse / Potential contaminant 列中值为”+“的蛋白')
    biomarker_label_free_norm = gol.get_value("biomarker_label_free_norm")
    gz.node('1', f'数据校正\n{biomarker_label_free_norm}-样本间（列）校正')

    biomarker_label_free_filter_index = gol.get_value("biomarker_label_free_filter_index")
    if biomarker_label_free_filter_index==0:
        biomarker_label_free_miss_n = gol.get_value("biomarker_label_free_miss_n")
        gz.node('2', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{biomarker_label_free_miss_n}过滤掉')
    else:
        biomarker_label_free_miss_ratio = gol.get_value("biomarker_label_free_miss_ratio")
        gz.node('2', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{biomarker_label_free_miss_ratio}%过滤掉')

    biomarker_label_free_imputation = gol.get_value("biomarker_label_free_imputation")
    gz.node('3', f'缺失值填补\n{biomarker_label_free_imputation}')
    biomarker_label_free_train_ratio = gol.get_value("biomarker_label_free_train_ratio")
    biomarker_label_free_test_ratio = gol.get_value("biomarker_label_free_test_ratio")
    biomarker_label_free_verification_ratio = gol.get_value("biomarker_label_free_verification_ratio")
    gz.node('4', f'数据集拆分比例\n训练集：{biomarker_label_free_train_ratio}，验证集：{biomarker_label_free_verification_ratio}，测试集：{biomarker_label_free_test_ratio}')
    biomarker_label_free_feature_select_index = gol.get_value("biomarker_label_free_feature_select_index")
    biomarker_label_free_feature_select = gol.get_value("biomarker_label_free_feature_select")
    biomarker_label_free_max_feature_num = gol.get_value("biomarker_label_free_max_feature_num")
    if biomarker_label_free_feature_select_index in [0,1,2,3,4]:
        biomarker_label_free_p = gol.get_value("biomarker_label_free_p")
        biomarker_label_free_fc = gol.get_value("biomarker_label_free_fc")
        p_threshold_index = gol.get_value("biomarker_label_free_p_threshold_index")
        if p_threshold_index == 0:
            gz.node('5',
                f'特征筛选-{biomarker_label_free_feature_select}\nP ≤ {biomarker_label_free_p} and {biomarker_label_free_fc}\n筛选后的特征数不多于:{biomarker_label_free_max_feature_num}')
        else:
            gz.node('5',
                    f'特征筛选-{biomarker_label_free_feature_select}\nFDR ≤ {biomarker_label_free_p} and {biomarker_label_free_fc}\n筛选后的特征数不多于:{biomarker_label_free_max_feature_num}')

    else:
        gz.node('5',f'特征筛选-{biomarker_label_free_feature_select}\n筛选后的特征数不多于:{biomarker_label_free_max_feature_num}')
    biomarker_label_free_classifier = gol.get_value("biomarker_label_free_classifier")
    gz.node('6', f'分类器算法\n{biomarker_label_free_classifier}')
    gz.edges(['01',"12", "23", "34","45","56"])
    gz.render(gv_path, format='png', view=False)
    return gv_path+".png"

def wgcna_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "wgcna.gv")

    gz = Digraph("wgcna", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)

    gz.node('0', '输入表达数据FPKM形式')
    gz.node('1', '过滤异常样本和异常基因')
    gz.node('2', '构建WGCNA网络，将基因划分为不同模块')
    gz.node('3', '找出与表型相关性最高的模块')
    gz.node('4', '找出该模块中的hub gene')
    gz.edge("0","1","保留FPKM的平均值>2的基因\nLog2(FPKM+1)")
    gz.edge("1","2","寻找最优软阈值\n(当样本量过低的情况，可能找不到最佳软阈值，无法构建WGCNA网络)")
    gz.edge("2","3","模块与表型进行显著性关联分析")
    gz.edge("3","4")
    gz.render(gv_path, format='png', view=False)
    return gv_path+".png"


def cox_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "cox.gv")

    gz = Digraph("cox", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)
    gz.node('0', '生存数据\n(单因素cox回归分析得到显著生存相关的基因表达文件)')

    gz.node('2', '多因素cox回归分析\n得到独立预后的因素')
    gz.node('3', '根据风险分数分为高低风险组')
    gz.node('4', '根据高低风险组绘制生存曲线、风险曲线、生存状态图和风险热图')
    gz.node('5', '绘制ROC曲线')
    multicox_if_enrich = gol.get_value("multicox_if_enrich")
    if multicox_if_enrich:
        # 进行lasso特征筛选
        gz.node('1', 'Lasso方法筛选')
        gz.edges(['01', "12", "23","34","45"])
    else:
        gz.edges(['02', "23","34","45"])
    gz.render(gv_path, format='png', view=False)
    return gv_path + ".png"


def label_free_pro_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path,"tmp","label_free_pro.gv")

    gz = Digraph("label_free_pro", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)

    gz.node('0', '（当为蛋白质组数据时）删除污染与反库蛋白\n删除 Reverse / Potential contaminant 列中值为”+“的蛋白')
    gz.node('1', '原始数据质量评估\n数据分布/数据缺失情况/样本相关性/样本聚类')
    label_free_pro_norm = gol.get_value("label_free_pro_norm")
    gz.node('2', f'数据校正\n{label_free_pro_norm}-样本间（列）校正')

    label_free_pro_filter_index = gol.get_value("label_free_pro_filter_index")
    if label_free_pro_filter_index==0:
        label_free_pro_miss_n = gol.get_value("label_free_pro_miss_n")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{label_free_pro_miss_n}过滤掉')
    else:
        label_free_pro_miss_ratio = gol.get_value("label_free_pro_miss_ratio")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{label_free_pro_miss_ratio}%过滤掉')

    label_free_pro_p = gol.get_value("label_free_pro_p")
    label_free_pro_fc = gol.get_value("label_free_pro_fc")
    label_free_pro_p_threshold_index = gol.get_value("label_free_pro_p_threshold_index")
    if label_free_pro_p_threshold_index == 0:
        gz.node('4', f'差异分析\nP ≤ {label_free_pro_p} and {label_free_pro_fc}；火山图，聚类图，热图')
    else:
        gz.node('4', f'差异分析\nFDR ≤ {label_free_pro_p} and {label_free_pro_fc}；火山图，聚类图，热图')

    label_free_pro_fill_index = gol.get_value("label_free_pro_fill_index")
    if label_free_pro_fill_index is not None and label_free_pro_fill_index!=0:
        label_free_pro_fill_text = gol.get_value("label_free_pro_fill_text")
        gz.node('6', f'缺失值填补\n{label_free_pro_fill_text}')
        gz.edges(['01', "23","36", "64"])
    else:
        gz.edges(['01', "23", "34"])
    label_free_pro_if_enrich = gol.get_value("label_free_pro_if_enrich")
    if label_free_pro_if_enrich:
        gz.node('5', f'富集分析\nGO富集分析、KEGG富集分析')
        gz.edge('4','5')
    gz.edge('1','2','如果有异常样本则删除(需手动)')
    gz.render(gv_path, format='png', view=False)
    return gv_path+".png"


def label_free_pho_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "label_free_pho.gv")

    gz = Digraph("label_free_pho", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)

    gz.node('0', '删除污染与反库的磷酸化肽段\n删除 Reverse / Potential contaminant 列中值为”+“的磷酸化肽段')
    gz.node('1', '原始数据质量评估\n数据分布/数据缺失情况/样本相关性/样本聚类')
    label_free_pho_norm = gol.get_value("label_free_pho_norm")
    gz.node('2', f'数据校正\n{label_free_pho_norm}-样本间（列）校正')

    label_free_pho_filter_index = gol.get_value("label_free_pho_filter_index")
    if label_free_pho_filter_index == 0:
        label_free_pho_miss_n = gol.get_value("label_free_pho_miss_n")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{label_free_pho_miss_n}过滤掉')
    else:
        label_free_pho_miss_ratio = gol.get_value("label_free_pho_miss_ratio")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{label_free_pho_miss_ratio}%过滤掉')

    label_free_pho_p = gol.get_value("label_free_pho_p")
    label_free_pho_fc = gol.get_value("label_free_pho_fc")
    label_free_pho_p_threshold_index = gol.get_value("label_free_pho_p_threshold_index")
    if label_free_pho_p_threshold_index == 0:
        gz.node('4', f'差异分析\n用蛋白质组的差异结果对磷酸化组的差异结果进行校正\nP ≤ {label_free_pho_p} and {label_free_pho_fc}；火山图，聚类图，热图')

    else:
        gz.node('4', f'差异分析\n用蛋白质组的差异结果对磷酸化组的差异结果进行校正\nFDR ≤ {label_free_pho_p} and {label_free_pho_fc}；火山图，聚类图，热图')

    label_free_pho_fill_index = gol.get_value("label_free_pho_fill_index")
    if label_free_pho_fill_index is not None and label_free_pho_fill_index != 0:
        label_free_pho_fill_text = gol.get_value("label_free_pho_fill_text")
        gz.node('6', f'缺失值填补\n{label_free_pho_fill_text}')
        gz.edges(['01', "23", "36", "64"])
    else:
        gz.edges(['01', "23", "34"])
    label_free_pho_if_enrich = gol.get_value("label_free_pho_if_enrich")
    if label_free_pho_if_enrich:
        gz.node('5', f'富集分析\nGO富集分析、KEGG富集分析')
        gz.edge('4', '5')
    gz.edge('1', '2', '如果有异常样本则删除(需手动)')
    gz.render(gv_path, format='png', view=False)
    return gv_path + ".png"


def marked_pho_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "marked_pho.gv")

    gz = Digraph("marked_pho", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)

    gz.node('0', '删除污染与反库的磷酸化肽段\n删除 Reverse / Potential contaminant 列中值为”+“的磷酸化肽段')
    gz.node('1', '原始数据质量评估\n数据分布/数据缺失情况/样本相关性/样本聚类')
    marked_pho_norm = gol.get_value("marked_pho_norm")
    gz.node('2', f'数据校正\n{marked_pho_norm}-样本间（列）校正/做ratio-磷酸化肽段（行）校正')

    marked_pho_filter_index = gol.get_value("marked_pho_filter_index")
    if marked_pho_filter_index == 0:
        marked_pho_miss_n = gol.get_value("marked_pho_miss_n")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{marked_pho_miss_n}过滤掉')
    else:
        marked_pho_miss_ratio = gol.get_value("marked_pho_miss_ratio")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{marked_pho_miss_ratio}%过滤掉')

    marked_pho_p = gol.get_value("marked_pho_p")
    marked_pho_fc = gol.get_value("marked_pho_fc")
    marked_pho_p_threshold_index = gol.get_value("marked_pho_p_threshold_index")
    if marked_pho_p_threshold_index == 0:
        gz.node('4',
                f'差异分析\n用蛋白质组的差异结果对磷酸化组的差异结果进行校正\nP ≤ {marked_pho_p} and {marked_pho_fc}；火山图，聚类图，热图')

    else:
        gz.node('4',
                f'差异分析\n用蛋白质组的差异结果对磷酸化组的差异结果进行校正\nFDR ≤ {marked_pho_p} and {marked_pho_fc}；火山图，聚类图，热图')

    marked_pho_fill_index = gol.get_value("marked_pho_fill_index")
    if marked_pho_fill_index is not None and marked_pho_fill_index != 0:
        marked_pho_fill_text = gol.get_value("marked_pho_fill_text")
        gz.node('6', f'缺失值填补\n{marked_pho_fill_text}')
        gz.edges(['01', "23", "36", "64"])
    else:
        gz.edges(['01', "23", "34"])
    marked_pho_if_enrich = gol.get_value("marked_pho_if_enrich")
    if marked_pho_if_enrich:
        gz.node('5', f'富集分析\nGO富集分析、KEGG富集分析')
        gz.edge('4', '5')
    gz.edge('1', '2', '如果有异常样本则删除(需手动)')
    gz.render(gv_path, format='png', view=False)
    return gv_path + ".png"


def marked_pro_flowchart():
    root_path = gol.get_value("RootPath")
    gv_path = os.path.join(root_path, "tmp", "marked_pro.gv")

    gz = Digraph("marked_pro", 'comment', None, None, 'png', None, "UTF-8",
                 {'rankdir': 'TB'},
                 {'color': 'black', 'fontcolor': 'black', 'fontname': 'Microsoft YaHei', 'fontsize': '12',
                  'style': 'rounded', 'shape': 'box'},
                 {'color': '#999999', 'fontcolor': 'black', 'fontsize': '10', 'fontname': 'Microsoft YaHei'}, None,
                 False)

    gz.node('0', '（当为蛋白质组数据时）删除污染与反库蛋白\n删除 Reverse / Potential contaminant 列中值为”+“的蛋白')
    gz.node('1', '原始数据质量评估\n数据分布/数据缺失情况/样本相关性/样本聚类')
    marked_pro_norm = gol.get_value("marked_pro_norm")
    gz.node('2', f'数据校正\n{marked_pro_norm}-样本间（列）校正/做ratio-蛋白（行）校正')

    marked_pro_filter_index = gol.get_value("marked_pro_filter_index")
    if marked_pro_filter_index == 0:
        marked_pro_miss_n = gol.get_value("marked_pro_miss_n")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中非缺失值数量低于{marked_pro_miss_n}过滤掉')
    else:
        marked_pro_miss_ratio = gol.get_value("marked_pro_miss_ratio")
        gz.node('3', f'缺失值过滤\n分组过滤，各组中缺失值比例高于{marked_pro_miss_ratio}%过滤掉')

    marked_pro_p = gol.get_value("marked_pro_p")
    marked_pro_fc = gol.get_value("marked_pro_fc")
    marked_pro_p_threshold_index = gol.get_value("marked_pro_p_threshold_index")
    if marked_pro_p_threshold_index == 0:
        gz.node('4', f'差异分析\nP ≤ {marked_pro_p} and {marked_pro_fc}；火山图，聚类图，热图')
    else:
        gz.node('4', f'差异分析\nFDR ≤ {marked_pro_p} and {marked_pro_fc}；火山图，聚类图，热图')

    marked_pro_fill_index = gol.get_value("marked_pro_fill_index")
    if marked_pro_fill_index is not None and marked_pro_fill_index != 0:
        marked_pro_fill_text = gol.get_value("marked_pro_fill_text")
        gz.node('6', f'缺失值填补\n{marked_pro_fill_text}')
        gz.edges(['01', "23", "36", "64"])
    else:
        gz.edges(['01', "23", "34"])
    marked_pro_if_enrich = gol.get_value("marked_pro_if_enrich")
    if marked_pro_if_enrich:
        gz.node('5', f'富集分析\nGO富集分析、KEGG富集分析')
        gz.edge('4', '5')
    gz.edge('1', '2', '如果有异常样本则删除(需手动)')
    gz.render(gv_path, format='png', view=False)
    return gv_path + ".png"

def scale_flowchart_png(flowchart_png_path):
    pil_image = QImage(flowchart_png_path)
    w_box = gol.get_value("window_width") * 0.35
    h_box = gol.get_value("window_height") * 0.35
    w, h = pil_image.width(), pil_image.height()  # 获取图像的原始大小
    f1 = 1.0 * w_box / w
    width = int(w * f1)
    height = int(h * f1)
    scale_image = pil_image.scaled(width, height)
    pix = QPixmap.fromImage(scale_image)
    return pix

def risk_model_flowchart():
    pass
