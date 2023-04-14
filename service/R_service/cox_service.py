from rpy2 import robjects
from util.Logger import logger
from rpy2.robjects import pandas2ri
import os
import util.Global as gol
from service.R_service.common_service import check_can_use_R


def unicox_service(unicox_data, unicox_result_path):
    check_can_use_R()
    pandas2ri.activate()
    robjects.r('''
                library(survival)
                library(ggplot2)
                library(grid)
                library(stringr)
            ''')
    logger.debug("单因素cox回归分析载入R包完成")

    r_unicox_data = pandas2ri.py2rpy(unicox_data)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file", "Rcode", "uniCox.R")
    rsource(codePath, encoding="utf-8")
    rsource(codePath)
    simple_cox = robjects.r("simple_cox")
    simple_cox(r_unicox_data,0.05,unicox_result_path)
    logger.debug("单因素cox回归分析分析完成")


def multicox_service(cox_data, cox_result_path,if_lasso):
    check_can_use_R()
    pandas2ri.activate()
    robjects.r('''
                library(glmnet)
                library(survival)
                library(survminer)
                library(pheatmap)
                library(timeROC)
                ''')
    logger.debug("多因素cox回归分析载入R包完成")

    cox_data = pandas2ri.py2rpy(cox_data)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file", "Rcode", "multiCox.R")
    rsource(codePath, encoding="utf-8")
    rsource(codePath)
    simple_cox = robjects.r("multi_cox")
    simple_cox(cox_data, 0.05, cox_result_path,if_lasso)
    logger.debug("多因素cox回归分析分析完成")