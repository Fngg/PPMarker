from rpy2 import robjects
from util.Logger import logger
import os
import util.Global as gol
from service.R_service.common_service import check_can_use_R
import re


def go_kegg_service(enrichOrgType,enrichGeneType,pre_genes,result_path):
    check_can_use_R()
    genes = []
    for pre_gene in pre_genes:
        if len(pre_gene) > 0:
            sub_gene_list = re.split(',|，|;', pre_gene)
            for sub_gene in sub_gene_list:
                if len(sub_gene.strip()) > 0:
                    genes.append(sub_gene)
    # 如果enrichOrgType == "mmu"  enrichGeneType == ”SYMBOL“要确保基因的名称是首字母大写，其他小写的形式
    modified_genes = []
    if enrichGeneType == "SYMBOL" and enrichOrgType == "mmu":
        for i in genes:
            modified_genes.append(str.capitalize(i))
    else:
        modified_genes = genes
    robjects.r('''
                library(org.Hs.eg.db)
                library(ggplot2)
                library(clusterProfiler)
                library(grid)
                library(enrichplot)
                library(GOplot)
                library(ComplexHeatmap)
                library(tidyverse)
            ''')
    logger.debug("富集分析载入R包完成")
    rgenes = robjects.FactorVector(modified_genes)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file","Rcode", "EnrichAnalysis.R")
    rsource(codePath, encoding="utf-8")
    # rsource(codePath)
    go_analysis = robjects.r("go_analysis")
    go_analysis(rgenes, enrichGeneType, enrichOrgType, result_path)
    logger.debug("go富集分析完成")
    kegg_analysis = robjects.r("kegg_analysis")
    kegg_analysis(rgenes, enrichGeneType, enrichOrgType, result_path)
    logger.debug("kegg富集分析完成")
    return True