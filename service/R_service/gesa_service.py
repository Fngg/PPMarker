from rpy2 import robjects
from util.Logger import logger
from rpy2.robjects import pandas2ri
import os
import util.Global as gol
from service.R_service.common_service import check_can_use_R

def gsea_service(enrichOrgType,enrichGeneType,data,result_path):
    check_can_use_R()
    pandas2ri.activate()
    robjects.r('''
                library(org.Hs.eg.db)
                library(ggplot2)
                library(clusterProfiler)
                library(grid)
                library(enrichplot)
                library(dplyr)
                library(data.table)
            ''')
    logger.debug("GSEA富集分析载入R包完成")
    r_data =pandas2ri.py2rpy(data)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file","Rcode", "GSEAAnalysis.R")
    rsource(codePath, encoding="utf-8")
    # rsource(codePath)
    gsea_go_analysis = robjects.r("gsea_go_analysis")
    gsea_go_analysis(r_data, enrichGeneType, enrichOrgType, result_path)
    logger.debug("go富集分析完成")
    kegg_analysis = robjects.r("gsea_kegg_analysis")
    kegg_analysis(r_data, enrichGeneType, enrichOrgType, result_path)
    logger.debug("kegg富集分析完成")
    return True