from rpy2 import robjects
import util.Global as gol
from util.Logger import logger
import os


def goOrKegg():
    enrichGeneFile = gol.get_value("EnrichGeneFile")
    enrichFilePath = gol.get_value("EnrichFilePath")
    if not enrichFilePath or not enrichGeneFile:
        logger.warning("没有导入数据或选择输出结果路径，无法进行富集分析")
        return False
    if os.path.exists(enrichGeneFile) and os.path.exists(enrichFilePath):
        enrichGeneType = gol.get_value("enrichGeneType")
        enrichOrgType = gol.get_value("enrichOrgType")
        pvalueCutoff = gol.get_value("pvalueCutoff")
        qvalueCutoff = gol.get_value("qvalueCutoff")
        EnrichType =  gol.get_value("EnrichType")
        robjects.r('''
            library(ggplot2)
            library(clusterProfiler)
            library(grid)
        ''')
        logger.debug("富集分析载入R包完成")
        rsource = robjects.r("source")
        codePath = os.path.join(gol.get_value("RootPath"), "Rcode", "Preprocess_ML_new", "mycode","EnrichAnalysis.R")
        rsource(codePath,encoding="utf-8")
        if EnrichType == "go":
            GoOnt = gol.get_value("GoOnt")
            go_analysis = robjects.r("go_analysis")
            go_analysis(enrichGeneFile,enrichGeneType,enrichOrgType,enrichFilePath,ont=GoOnt,
                        pvalueCutoff=pvalueCutoff,qvalueCutoff=qvalueCutoff)
        else:
            kegg_analysis = robjects.r("kegg_analysis")
            kegg_analysis(enrichGeneFile,enrichGeneType,enrichOrgType,enrichFilePath,pvalueCutoff=pvalueCutoff,qvalueCutoff=qvalueCutoff)
        return True
    return False


def wgcna1():
    '''
    数据导入与数据清洗
    :return:
    '''
    WgcnaExpressionFile = gol.get_value("WgcnaExpressionFile")
    WgcnaTraitFile = gol.get_value("WgcnaTraitFile")
    WGCNAFilePath = gol.get_value("WGCNAFilePath")
    if not WgcnaExpressionFile or not WgcnaTraitFile or not WGCNAFilePath:
        logger.warning("没有导入数据或选择输出结果路径，无法进行WGCNA分析")
        return False
    if os.path.exists(WgcnaExpressionFile) and os.path.exists(WgcnaTraitFile) and os.path.exists(WGCNAFilePath):
        robjects.r('''
            library(WGCNA)
            library(grid)
            options(stringsAsFactors = FALSE);
            library(stringr)
        ''')
        logger.debug("WGCNA分析载入R包完成")
        rsource = robjects.r("source")
        codePath = os.path.join(gol.get_value("RootPath"), "Rcode", "Preprocess_ML_new", "mycode","WGCNA.R")
        rsource(codePath,encoding="utf-8")
        preprocess = robjects.r("preprocess")
        data_list = preprocess(WgcnaExpressionFile,WgcnaTraitFile,WGCNAFilePath)
        gol.set_value("WGCNADataList",data_list)
        return True
    return False


def wgcna2():
    '''
    无尺度网络构建
    :return:
    '''
    data_list = gol.get_value("WGCNADataList")
    WGCNAFilePath = gol.get_value("WGCNAFilePath")
    if data_list and WGCNAFilePath:
        network_construction = robjects.r("network_construction")
        net_list = network_construction(data_list,WGCNAFilePath)
        gol.set_value("WGCNANetList",net_list)
        return True
    return False


def wgcna3():
    '''
    探究模型与性状，基因与性状
    :return:
    '''
    data_list = gol.get_value("WGCNADataList")
    net_list = gol.get_value("WGCNANetList")
    WGCNAFilePath = gol.get_value("WGCNAFilePath")
    trait = gol.get_value("SelectedTrait")
    if data_list and net_list and WGCNAFilePath and trait:
        explore_model = robjects.r("explore_model")
        net_list = explore_model(data_list,net_list,trait,WGCNAFilePath)
        return True
