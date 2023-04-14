from rpy2 import robjects
from util.Logger import logger
from rpy2.robjects import pandas2ri
import os
import util.Global as gol
from service.R_service.common_service import check_can_use_R


def wgcna_service(wgcna_expression_df, wgcna_information_df2, wgcna_interested_trait, wgcna_result_path):
    check_can_use_R()
    pandas2ri.activate()
    robjects.r('''
                library(WGCNA)
                library(ggplot2)
                library(grid)
                library(stringr)
            ''')
    logger.debug("WGCNA载入R包完成")

    r_wgcna_expression = pandas2ri.py2rpy(wgcna_expression_df)
    r_wgcna_information = pandas2ri.py2rpy(wgcna_information_df2)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file", "Rcode", "WGCNAAnalysis.R")
    rsource(codePath, encoding="utf-8")
    rsource(codePath)
    wgcna_analysis = robjects.r("wgcna_analysis")
    wgcna_analysis(r_wgcna_expression, r_wgcna_information, wgcna_result_path, wgcna_interested_trait)
    logger.debug("WGCNA分析完成")
