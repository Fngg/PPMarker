'''
无标记定量的蛋白质组学质谱数据处理流程
'''
from PyQt5.QtCore import QThread, pyqtSignal
import time, os

from service.R_service.go_kegg_service import go_kegg_service
from service.R_service.r_heatmap_service import draw_r_heatmap_service
from service.difference_analysis.BaseProPhoService import pho_dfp_base_pro
from service.picture.r_plot_service import heatmap_service
from util.Logger import logger
import util.Global as gol
from service.FileService import readFile
from service.difference_analysis.UtilService import check_data_label_free_pho, create_result_dir, get_groups_dict_list, export_data,extract_gene_name
from service.difference_analysis.DropConRevService import drop_CON_REV
from service.PdfService import ResultPdf
from service.difference_analysis.NormalizationService import upper_quantile_norm, quantile_norm, flatten_sum_norm, \
    FOT_norm
from service.difference_analysis.MissingService import filter_by_n, base_missing_filing, filter_by_ratio, \
    knn_missing_filter, forest_missing_filing
from service.difference_analysis.DifferenceAnalysisService import dfp_analysis
from service.difference_analysis.VisualizationService import data_assesment, data_norm, data_filter, data_dfp_analysis, \
    data_imputation
from config.global_config import Normalization_and_Filtering_dirname, Difference_Analysis_dirname, \
    Enrichment_Analysis_dirname
import pandas as pd


class LabelFreePhoQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(LabelFreePhoQThread, self).__init__()
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
        logger.debug("无标记定量磷酸化组学分析开始")
        label_free_pho_expression_path = gol.get_value("label_free_pho_expression_path")
        label_free_pho_information_path = gol.get_value("label_free_pho_information_path")
        label_free_pho_prodata_path = gol.get_value("label_free_pho_prodata_path")
        label_free_pho_result_path = gol.get_value("label_free_pho_result_path")
        if_enrich = gol.get_value("label_free_pho_if_enrich")
        if_gene_name = gol.get_value("label_free_pho_if_gene_name")
        if if_gene_name:
            gene_col_name = gol.get_value("label_free_pho_gene_name")
        else:
            gene_col_name = "Gene names"
        # pdf记录分析过程
        pdf_path = os.path.join(label_free_pho_result_path, "readme.pdf")
        self.pdf = ResultPdf(pdf_path, "无标记定量磷酸化组学数据分析结果")

        # 创建结果文件夹
        create_result_dir(label_free_pho_result_path,if_enrich)

        expression_df = readFile(label_free_pho_expression_path,if_zero_na=True, index_col=None)
        information_df = readFile(label_free_pho_information_path,if_zero_na=False, index_col=None)
        pro_dfp_df = readFile(label_free_pho_prodata_path,sheet_name=0,if_zero_na=False)
        pro_supplementary_df = readFile(label_free_pho_prodata_path,sheet_name=1,if_zero_na=False)
        # 检测数据是否符合要求
        result, despri = check_data_label_free_pho(expression_df, information_df,pro_dfp_df,pro_supplementary_df)
        if not result:
            self.error_trigger.emit(despri)
            self.pdf.add_simple_content(despri)
            self.over(start_time, False)
            return None
        # 针对PD的数据，需要从 Description 列中提取 ”Gene names“
        expression_df = extract_gene_name(expression_df)
        # 修改表达数据的行名与列名
        if gene_col_name in expression_df.columns:
            expression_df[gene_col_name].fillna("", inplace=True)
            expression_df.index = expression_df.apply(lambda row:  str(row[gene_col_name]) + "_" + str(row.name), axis=1)
            expression_df.index.name = "Gene names_No."
        else:
            expression_df.index.name = "No."
        logger.debug("删除污染与反库的磷酸化肽段")
        # 删除污染与反库蛋白
        expression_df, despri = drop_CON_REV(expression_df)
        self.info_record("删除污染与反库的磷酸化肽段", despri)
        # 更改列名
        logger.debug("更改列名")
        complement_expression_df = expression_df.drop(information_df["id"], axis=1)
        expression_df = expression_df.loc[:, information_df["id"]]
        expression_df.columns = information_df["name"]

        groups_dict, groups, simples = get_groups_dict_list(information_df)
        # 数据质量评估
        data_assesment(expression_df, label_free_pho_result_path, groups_dict,groups,simples)
        self.info_record("数据质量评估", "生成数据分布/数据缺失情况/样本相关性/样本聚类等图")
        # 校正
        norm_index = gol.get_value("label_free_pho_norm_index")
        if norm_index == 0:
            label_free_pho_norm = "upper quantile normalization"
            expression_norm_df = upper_quantile_norm(expression_df)
        elif norm_index == 1:
            label_free_pho_norm = "quantile normalization"
            expression_norm_df = quantile_norm(expression_df)
        elif norm_index ==3:
            label_free_pho_norm = "flatten sum normalization"
            expression_norm_df = flatten_sum_norm(expression_df)
        elif norm_index==4:
            label_free_pho_norm = "FOT normalization"
            expression_norm_df = FOT_norm(expression_df)
        else:
            label_free_pho_norm = "no normalization"
            expression_norm_df = expression_df
        if label_free_pho_norm != "no normalization":
            self.info_record("数据校正", label_free_pho_norm + "-样本间（列）校正")
            data_norm(expression_df, expression_norm_df, label_free_pho_norm, label_free_pho_result_path,groups_dict)
            export_data(expression_norm_df, label_free_pho_result_path, Normalization_and_Filtering_dirname,
                        "alfter_normalization.xlsx", label_free_pho_norm)

        # 数据过滤
        filter_index = gol.get_value("label_free_pho_filter_index")
        if filter_index == 0:
            miss_n = gol.get_value("label_free_pho_miss_n")
            expression_filter_df = filter_by_n(expression_norm_df, miss_n, groups)
            filter_rule = f"各组中非缺失值数量低于{miss_n}过滤掉"
        elif filter_index == 1:
            miss_ratio = gol.get_value("label_free_pho_miss_ratio")
            if miss_ratio > 1:
                miss_ratio = float(miss_ratio / 100)
            expression_filter_df = filter_by_ratio(expression_norm_df, miss_ratio, groups)
            filter_rule = f"各组中缺失值比例高于{miss_ratio}%过滤掉"
        else:
            raise Exception("The selected missing value filtering rule is out of range")
        filter_row_num = len(expression_norm_df) - len(expression_filter_df)
        self.info_record("数据过滤", "分组过滤，" + filter_rule + "，一共过滤掉" + str(filter_row_num) + "行。")
        export_data(expression_filter_df, label_free_pho_result_path, Normalization_and_Filtering_dirname,
                    "alfter_normalization_and_filter.xlsx", "normalization and filter data")
        data_filter(expression_norm_df, expression_filter_df, None, label_free_pho_result_path, groups_dict)

        # 缺失值填补
        fill_index = gol.get_value("label_free_pho_fill_index")
        fill_text = gol.get_value("label_free_pho_fill_text")
        if fill_index == 0:
            # 不填补
            label_free_imputation = "Not filling"
            expression_imputation_df = expression_filter_df
        elif fill_index == 1:
            # 最小值填补
            label_free_imputation = "minimum filling"
            expression_imputation_df = base_missing_filing(expression_filter_df, groups=groups)
        elif fill_index == 2:
            # k近邻填补
            label_free_imputation = "KNN filling"
            expression_imputation_df = knn_missing_filter(expression_filter_df)
        else:
            # 随机森林填补
            label_free_imputation = "random forest filling"
            expression_imputation_df = forest_missing_filing(expression_filter_df)
        if fill_index != 0:
            self.info_record("缺失值填补", fill_text)
            data_imputation(expression_filter_df, expression_imputation_df, label_free_imputation,
                            label_free_pho_result_path, groups_dict, Normalization_and_Filtering_dirname)
            export_data(expression_imputation_df, label_free_pho_result_path, Normalization_and_Filtering_dirname,
                        "normalization_filter_imputation.xlsx", "normalization_filter_imputation")

        # 差异蛋白分析
        fc_index = gol.get_value("label_free_pho_fc_index")
        fc_despri = gol.get_value("label_free_pho_fc")
        if fc_index == 0:
            fc = 1.5
        elif fc_index == 1:
            fc = 1.25
        elif fc_index == 2:
            fc = 2
        elif fc_index == 3:
            fc = 3
        elif fc_index == 4:
            fc = 4
        else:
            raise Exception("差异倍数FC的范围取值异常")
        pgroup = gol.get_value("label_free_pho_pgroup") # 阳性组
        pro_p_threshold_index = gol.get_value("label_free_pho_p_threshold_index")
        p = gol.get_value("label_free_pho_p")  # P值or FDR值
        if pro_p_threshold_index == 0:
            if_p = True
            p_despri = f"P ≤ {p},"
            pvalue_colname = "Pvalue"
        else:
            if_p = False  # 选择FDR值
            p_despri = f"FDR ≤ {p},"
            pvalue_colname = "fdr"

        analysis = dfp_analysis(expression_imputation_df, groups_dict, FC_threshold=fc, E_group=pgroup,p=float(p),if_p=if_p)
        all = pd.merge(expression_imputation_df, analysis, left_index=True, right_index=True)
        # 与蛋白组的差异表达结果做校正
        finally_all = pho_dfp_base_pro(all,complement_expression_df.loc[all.index, :],pro_dfp_df,pro_supplementary_df,fc,p=float(p),pvalue_colname=pvalue_colname)

        up_genes_len = len(finally_all[finally_all["finally_DEP"] == "up-regulated"])
        down_genes_len = len(finally_all[finally_all["finally_DEP"] == "down-regulated"])
        self.info_record("差异分析",
                         p_despri + fc_despri + "; 可视化展示：火山图，聚类图，热图。\n一共得到差异上调基因" + str(
                             up_genes_len) + "个，差异下调基因" + str(down_genes_len) + "个。")

        export_data(finally_all, label_free_pho_result_path, Difference_Analysis_dirname,
                    "difference_analysis.xlsx", "difference analysis result data",
                    complement_expression_df.loc[finally_all.index, :])

        data_dfp_analysis(finally_all,fc,groups,simples,groups_dict,label_free_pho_result_path,pvalue_colname=pvalue_colname,log2fc_colname = "finally_log2FC",dfp_colname="finally_DEP",p_value=float(p))

        # tmp = base_missing_filing(finally_all, groups=groups)
        # tmp["DEP"] = finally_all.loc[tmp.index, "finally_DEP"].to_list()
        # if "Gene names" in complement_expression_df.columns:
        #     tmp.index = complement_expression_df.loc[tmp.index, "Gene names"]
        # heatmap_result_path = os.path.join(label_free_pho_result_path, Difference_Analysis_dirname)
        # result = draw_r_heatmap_service(tmp[tmp["DEP"] != "none-significant"], groups_dict, simples, heatmap_result_path)
        # if result:
        #     self.info_record("R绘制热图","完成")
        if if_enrich:
            if "Gene names_No." == finally_all.index.name:
                enrichOrgType = gol.get_value("label_free_pho_org_type")
                enrichGeneType = gol.get_value("label_free_pho_gene_type")
                self.info_record("富集分析", "差异上下调基因分别做Go和KEGG富集分析")
                up_genes = []
                for gene_no in finally_all.loc[finally_all["finally_DEP"]=="up-regulated"].index:
                    gene = gene_no.rsplit("_", 1)[0].strip()
                    if len(gene)>0:
                        up_genes.append(gene)
                if len(up_genes)>0:
                    enrich_result_path_up = os.path.join(label_free_pho_result_path, Enrichment_Analysis_dirname,"up")
                    go_kegg_service(enrichOrgType, enrichGeneType, up_genes, enrich_result_path_up)
                down_genes = []
                for gene_no in finally_all.loc[finally_all["finally_DEP"]=="down-regulated"].index:
                    gene = gene_no.rsplit("_", 1)[0].strip()
                    if len(gene)>0:
                        down_genes.append(gene)
                if len(down_genes)>0:
                    enrich_result_path_down = os.path.join(label_free_pho_result_path, Enrichment_Analysis_dirname, "down")
                    go_kegg_service(enrichOrgType, enrichGeneType, down_genes, enrich_result_path_down)
        # 运行结束
        self.over(start_time, True)
