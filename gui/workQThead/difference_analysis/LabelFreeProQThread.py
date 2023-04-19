'''
无标记定量的蛋白质组学质谱数据处理流程
'''
from PyQt5.QtCore import QThread, pyqtSignal
import time, os

from service.R_service.go_kegg_service import go_kegg_service
from service.R_service.r_heatmap_service import draw_r_heatmap_service
from util.Logger import logger
import util.Global as gol
from service.FileService import readFile
from service.difference_analysis.UtilService import check_data_label_free_pro, create_result_dir, get_groups_dict_list, \
    export_data, extract_gene_name
from service.difference_analysis.DropConRevService import drop_CON_REV
from service.PdfService import ResultPdf
from service.difference_analysis.NormalizationService import upper_quantile_norm, quantile_norm, flatten_sum_norm, \
    FOT_norm
from service.difference_analysis.MissingService import filter_by_n, base_missing_filing, filter_by_ratio, \
    knn_missing_filter, forest_missing_filing
from service.difference_analysis.DifferenceAnalysisService import dfp_analysis, dfp_analysis_correlation
from service.difference_analysis.VisualizationService import data_assesment, data_norm, data_filter, data_dfp_analysis, \
    data_imputation
from config.global_config import Normalization_and_Filtering_dirname, Difference_Analysis_dirname, \
    Enrichment_Analysis_dirname
import pandas as pd
import numpy as np


class LabelFreeProQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(LabelFreeProQThread, self).__init__()
        self.pdf = None
        self.i = 0

    def over(self, start_time, if_sucess):
        '''
        结束时执行的操作
        '''
        end_time = time.time()
        if if_sucess:
            text = "数据分析运行成功,"
        else:
            text = "数据分析运行失败,"
        self.info_trigger.emit(text, "总时长为：" + str(end_time - start_time) + " s")
        # 创建pdf
        self.pdf.create()

    def info_record(self, step, text):
        self.info_trigger.emit(step, text)
        self.pdf.add_content(step, text)

    def run(self):
        try:
            self._run()
        except Exception as e:
            # 日志记录
            logger.exception("Exception Logged")
            # self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            msg = repr(e)
            if "Permission" in msg:
                if ".xlsx" in str(e):
                    msg = "生成的excel结果文件已经打开，请先关闭excel文件"
                elif ".pdf" in str(e):
                    msg = "生成的PDF结果文件已经打开，请先关闭PDF文件"
                else:
                    msg = "生成的结果文件已经打开，请先关闭相应的文件"
            self.error_trigger.emit(msg)
            self.pdf.create()

    def _run(self):
        start_time = time.time()
        logger.debug("无标记定量蛋白质组学分析开始")
        label_free_pro_expression_path = gol.get_value("label_free_pro_expression_path")
        label_free_pro_information_path = gol.get_value("label_free_pro_information_path")
        label_free_pro_result_path = gol.get_value("label_free_pro_result_path")
        if_enrich = gol.get_value("label_free_pro_if_enrich")
        # pdf记录分析过程
        pdf_path = os.path.join(label_free_pro_result_path, "readme.pdf")
        self.pdf = ResultPdf(pdf_path, "无标记定量蛋白质组学数据分析结果")

        # 创建结果文件夹
        create_result_dir(label_free_pro_result_path,if_enrich)

        expression_df = readFile(label_free_pro_expression_path,if_zero_na=True, index_col=None)
        information_df = readFile(label_free_pro_information_path,if_zero_na=False, index_col=None)
        information_df.sort_values(["group", "name"], inplace=True, ascending=True)
        # 检测数据是否符合要求
        result, despri = check_data_label_free_pro(expression_df, information_df)
        if not result:
            self.error_trigger.emit(despri)
            self.pdf.add_simple_content(despri)
            self.over(start_time, False)
            return None
        # 针对PD的数据，需要从 Description 列中提取 ”Gene names“
        expression_df = extract_gene_name(expression_df)
        # 修改表达数据的行名与列名
        if "Gene names" in expression_df.columns:
            expression_df["Gene names"].fillna("", inplace=True)
            expression_df.index = expression_df.apply(lambda row:  str(row["Gene names"]) + "_" + str(row.name), axis=1)
            expression_df.index.name = "Gene names_No."
        else:
            expression_df.index.name = "No."
        logger.debug("删除污染与反库蛋白")
        # 删除污染与反库蛋白
        expression_df, despri = drop_CON_REV(expression_df)
        self.info_record("删除污染与反库蛋白", despri)
        # 更改列名
        logger.debug("更改列名")
        complement_expression_df = expression_df.drop(information_df["id"], axis=1)
        expression_df = expression_df.loc[:, information_df["id"]]
        expression_df.columns = information_df["name"]

        groups_dict, groups, simples = get_groups_dict_list(information_df)
        # 数据质量评估
        data_assesment(expression_df, label_free_pro_result_path, groups_dict,groups,simples)
        self.info_record("数据质量评估", "生成数据分布/数据缺失情况/样本相关性/样本聚类等图")
        # 校正
        norm_index = gol.get_value("label_free_pro_norm_index")
        if norm_index == 0:
            label_free_pro_norm = "upper quantile normalization"
            expression_norm_df = upper_quantile_norm(expression_df)
        elif norm_index == 1:
            label_free_pro_norm = "quantile normalization"
            expression_norm_df = quantile_norm(expression_df)
        elif norm_index ==3:
            label_free_pro_norm = "flatten sum normalization"
            expression_norm_df = flatten_sum_norm(expression_df)
        elif norm_index==4:
            label_free_pro_norm = "FOT normalization"
            expression_norm_df = FOT_norm(expression_df)
        else:
            label_free_pro_norm = "no normalization"
            expression_norm_df = expression_df
        if label_free_pro_norm !="no normalization":
            self.info_record("数据校正", label_free_pro_norm + "-样本间（列）校正")
            data_norm(expression_df, expression_norm_df, label_free_pro_norm, label_free_pro_result_path,groups_dict)
            export_data(expression_norm_df, label_free_pro_result_path, Normalization_and_Filtering_dirname,
                        "alfter_normalization.xlsx", label_free_pro_norm)

        # 数据过滤
        filter_index=gol.get_value("label_free_pro_filter_index")
        if filter_index==0:
            miss_n = gol.get_value("label_free_pro_miss_n")
            expression_filter_df = filter_by_n(expression_norm_df, miss_n, groups)
            filter_rule = f"各组中非缺失值数量低于{miss_n}过滤掉"
        elif filter_index==1:
            miss_ratio = gol.get_value("label_free_pro_miss_ratio")
            if miss_ratio > 1:
                miss_ratio = float(miss_ratio / 100)
            expression_filter_df = filter_by_ratio(expression_norm_df,miss_ratio,groups)
            filter_rule =f"各组中缺失值比例高于{miss_ratio}%过滤掉"
        else:
            raise Exception("The selected missing value filtering rule is out of range")
        filter_row_num = len(expression_norm_df) - len(expression_filter_df)
        self.info_record("数据过滤","分组过滤，"+filter_rule+"，一共过滤掉"+str(filter_row_num)+"行。")
        export_data(expression_filter_df, label_free_pro_result_path, Normalization_and_Filtering_dirname,
                    "alfter_normalization_and_filter.xlsx", "normalization and filter data")
        data_filter(expression_norm_df, expression_filter_df, None, label_free_pro_result_path, groups_dict)

        # 缺失值填补
        fill_index= gol.get_value("label_free_pro_fill_index")
        fill_text= gol.get_value("label_free_pro_fill_text")
        if fill_index == 0:
            # 不填补
            label_free_imputation = "Not filling"
            expression_imputation_df = expression_filter_df
        elif fill_index == 1:
            # 最小值填补
            label_free_imputation = "minimum filling"
            expression_imputation_df = base_missing_filing(expression_filter_df,groups=groups)
        elif fill_index==2:
            # k近邻填补
            label_free_imputation = "KNN filling"
            expression_imputation_df = knn_missing_filter(expression_filter_df)
        else:
            # 随机森林填补
            label_free_imputation = "random forest filling"
            expression_imputation_df = forest_missing_filing(expression_filter_df)
        if fill_index!=0:
            self.info_record("缺失值填补", fill_text)
            data_imputation(expression_filter_df, expression_imputation_df, label_free_imputation, label_free_pro_result_path, groups_dict,Normalization_and_Filtering_dirname)
            export_data(expression_imputation_df, label_free_pro_result_path, Normalization_and_Filtering_dirname,
                        "normalization_filter_imputation.xlsx", "normalization_filter_imputation")

        # 差异蛋白分析
        fc_index = gol.get_value("label_free_pro_fc_index")
        fc_despri = gol.get_value("label_free_pro_fc")
        if fc_index==0:
            fc = 1.5
        elif fc_index==1:
            fc=1.25
        elif fc_index ==2:
            fc = 2
        elif fc_index==3:
            fc = 3
        elif fc_index==4:
            fc=4
        else:
            raise Exception("差异倍数FC的范围取值异常")
        # 差异分析
        if_correlation = gol.get_value("label_free_pro_if_correlation")
        pgroup = gol.get_value("label_free_pro_pgroup") # 阳性组
        pro_p_threshold_index = gol.get_value("label_free_pro_p_threshold_index")
        p = gol.get_value("label_free_pro_p")  # P值or FDR值
        if pro_p_threshold_index==0:
            if_p = True
            p_despri=f"P ≤ {p},"
            pvalue_colname = "Pvalue"
        else:
            if_p = False # 选择FDR值
            p_despri = f"FDR ≤ {p},"
            pvalue_colname = "fdr"
        if if_correlation is not None and if_correlation==True:
            # 配对样本检验
            correlation_dict = gol.get_value("label_free_pro_correlation_dict")
            # analysis = dfp_analysis_correlation(expression_imputation_df, groups_dict,correlation_dict, FC_threshold=fc, E_group=pgroup,p=float(p),already_log2=True)
            analysis = dfp_analysis_correlation(expression_imputation_df, groups_dict,correlation_dict, FC_threshold=fc, E_group=pgroup,p=float(p),if_p=if_p)
        else:
            # 非配对样本检验
            # analysis = dfp_analysis(expression_imputation_df, groups_dict, FC_threshold=fc, E_group=pgroup,p=float(p),already_log2=True)
            analysis = dfp_analysis(expression_imputation_df, groups_dict, FC_threshold=fc, E_group=pgroup,p=float(p),if_p=if_p)
        all = pd.merge(expression_imputation_df, analysis, left_index=True, right_index=True)
        up_genes_len = len(analysis[analysis["DEP"] == "up-regulated"])
        down_genes_len = len(analysis[analysis["DEP"] == "down-regulated"])
        self.info_record("差异分析",p_despri+fc_despri+"; 可视化展示：火山图，聚类图，热图。\n一共得到差异上调基因"+str(up_genes_len)+"个，差异下调基因"+str(down_genes_len)+"个。")
        export_data(all, label_free_pro_result_path, Difference_Analysis_dirname,
                    "difference_analysis.xlsx", "difference analysis result data",
                    complement_expression_df.loc[all.index, :])
        data_dfp_analysis(all,fc,groups,simples,groups_dict,label_free_pro_result_path,p_value=float(p),pvalue_colname=pvalue_colname)

        # tmp = base_missing_filing(all, groups=groups)
        # tmp["DEP"] = all.loc[tmp.index,"DEP"].to_list()
        # if "Gene names" in complement_expression_df.columns:
        #     tmp.index = complement_expression_df.loc[tmp.index, "Gene names"]
        # heatmap_result_path = os.path.join(label_free_pro_result_path, Difference_Analysis_dirname)
        # result = draw_r_heatmap_service(tmp[tmp["DEP"]!="none-significant"],groups_dict,simples,heatmap_result_path)
        # if result:
        #     self.info_record("R绘制热图","完成")
        # 富集分析
        if if_enrich:
            if "Gene names_No." == all.index.name:
                enrichOrgType = gol.get_value("label_free_pro_org_type")
                enrichGeneType = gol.get_value("label_free_pro_gene_type")
                self.info_record("富集分析", "差异上下调基因分别做Go和KEGG富集分析")
                up_genes = []
                for gene_no in all.loc[all["DEP"]=="up-regulated"].index:
                    gene = gene_no.rsplit("_", 1)[0].strip()
                    if len(gene)>0:
                        up_genes.append(gene)
                if len(up_genes)>0:
                    enrich_result_path_up = os.path.join(label_free_pro_result_path, Enrichment_Analysis_dirname,"up")
                    go_kegg_service(enrichOrgType, enrichGeneType, up_genes, enrich_result_path_up)
                down_genes = []
                for gene_no in all.loc[all["DEP"]=="down-regulated"].index:
                    gene = gene_no.rsplit("_", 1)[0].strip()
                    if len(gene)>0:
                        down_genes.append(gene)
                if len(down_genes)>0:
                    enrich_result_path_down = os.path.join(label_free_pro_result_path, Enrichment_Analysis_dirname, "down")
                    go_kegg_service(enrichOrgType, enrichGeneType, down_genes, enrich_result_path_down)
        # 运行结束
        self.over(start_time, True)
