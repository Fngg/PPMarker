'''
DIA 原始数据转为 以precursors或protein.groups为行，以样本为列的二维矩阵
'''
from util.Logger import logger
from service.FileService import readFile
import numpy as np
import pandas as pd
from service.dia_analysis.DIANNService import maxlfq_solve
from PyQt5.QtCore import QThread, pyqtSignal
import time, os
import util.Global as gol


class DIAQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(DIAQThread, self).__init__()

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

    def info_record(self, step, text):
        self.info_trigger.emit(step, text)

    def run(self):
        try:
            self._run()
        except Exception as e:
            # 日志记录
            logger.exception("Exception Logged")
            # self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            msg = repr(e)
            if "Permission" in msg:
                msg = "生成的excel结果文件已经打开，请先关闭excel文件"
            self.error_trigger.emit(msg)

    def _run(self):
        start_time = time.time()
        logger.debug("DIA数据处理分析开始")
        diann_expression_data_path = gol.get_value("diann_expression_data_path")
        dia_result_path = gol.get_value("dia_result_path")
        protein_group_header = gol.get_value("dia_protein_group_header")
        diann_simple_name_path = gol.get_value("diann_simple_name_path")
        # 先读取第一行的数据，就是列名
        col_names_df = readFile(diann_expression_data_path,if_zero_na=False, index_col=False, header=None, nrows=1)
        # 先检查必须存在的这几列有没有：Precursor.Id，Precursor.Normalised，File.Name，Protein.Group/Protein.Names
        need_cols = ["File.Name", protein_group_header, "Precursor.Id", "Precursor.Normalised"]
        if not set(need_cols).issubset(col_names_df.iloc[0, :].values):
            despri = "必须存在的4列没有"
            self.error_trigger.emit(despri)
            self.over(start_time, False)
            return None
        other_clos = ["PG.Q.Value", "Q.Value", "Genes", "First.Protein.Description"]
        need_other_clos = self.get_exist_cols(col_names_df.iloc[0, :].values, other_clos)
        usecols = need_other_clos + need_cols  # 需要读取的列

        df = readFile(diann_expression_data_path,if_zero_na=False, index_col=False, usecols=usecols)
        df.dropna(subset=["File.Name"],inplace=True)
        if diann_simple_name_path:
            # 替换File.Name为样本名称
            diann_simple_name_df = self.check_diann_simple_file(df,diann_simple_name_path)
            if diann_simple_name_df is not None:
                df["File.Name"] = df["File.Name"].apply(lambda x:diann_simple_name_df.loc[x,"simple"])
            else:
                self.info_record("File.Name转换样本名称失败", diann_simple_name_path+"文件中没有所有的File.Name对应的样本名称")
        # PG.Q.Value<=0.01  和Q.Value<=0.01进行过滤掉质量不好的数据
        if "PG.Q.Value" in df.columns:
            df = df[df["PG.Q.Value"] <= 0.01]
            need_other_clos.remove("PG.Q.Value")
        if "Q.Value" in df.columns:
            df = df[df["Q.Value"] <= 0.01]
            need_other_clos.remove("Q.Value")
        # dataframe 中数据类型转换
        for col in usecols:
            if col in ["PG.Q.Value", "Q.Value", "Precursor.Normalised"]:
                df[col] = df[col].astype('float')
            else:
                df[col] = df[col].astype('str')
        # Precursor.Id  != '' & df[Precursor.Normalised] > 0
        df = df[(df["Precursor.Id"] != '') & (df["Precursor.Normalised"] > 0) & (df[protein_group_header] != '')]
        # 查询是否有重复数据
        is_duplicated = any((df["File.Name"] + ":" + df["Precursor.Id"]).duplicated())
        if is_duplicated:
            print("Multiple quantities per id (File.Name and Precursor.Id): the maximum of these will be calculated")
        precursors_df = df.pivot_table(index='Precursor.Id', columns='File.Name', values='Precursor.Normalised',
                                       aggfunc=np.max)

        precursors_result_path = os.path.join(dia_result_path,"precursors.csv")
        for col in need_other_clos:
            precursors_df[col] = precursors_df.apply(lambda x:df.loc[df["Precursor.Id"] == x.name, col].iloc[0],axis=1)
        precursors_df.to_csv(precursors_result_path)


        protein_df = self.protein(df, protein_group_header, margin=-10)
        protein_result_path = os.path.join(dia_result_path, "protein.csv")
        for col in need_other_clos:
            protein_df[col] = protein_df.apply(lambda x:df.loc[df[protein_group_header]==x.name,col].iloc[0],axis=1)
        protein_df.to_csv(protein_result_path)
        # 运行结束
        self.over(start_time, True)

    def check_diann_simple_file(self,df,diann_simple_name_path):
        '''
        检查File.Name是否diann样本名称文件存在对应的样本名称
        '''
        diann_simple_name_df = readFile(diann_simple_name_path,if_zero_na=False)
        file_names = df["File.Name"].dropna().unique()
        if not set(file_names).issubset(diann_simple_name_df.index):
            return None
        else:
            return diann_simple_name_df

    def get_exist_cols(self, col_names,cols_list):
        '''
        返回cols_list中在data_df中存在的列
        '''
        result = []
        for i in cols_list:
            if i in col_names:
                result.append(i)
        return result

    def protein(self,data_df, protein_group_header, margin=-10):
        if margin > -2:
            margin = -2
        elif margin < -20:
            margin = -20
        data_df["Precursor.Normalised"] = np.log(data_df["Precursor.Normalised"])
        data_df.loc[data_df["Precursor.Normalised"] <= margin, "Precursor.Normalised"] = np.nan
        data_df = data_df.dropna(subset=["Precursor.Normalised"])
        proteins = data_df[protein_group_header].unique()
        m = len(proteins)
        samples = data_df["File.Name"].unique()
        result = pd.DataFrame(index=proteins, columns=samples)
        for i in range(m):
            piv = data_df[data_df[protein_group_header] == proteins[i]].pivot_table(index='Precursor.Id',
                                                                                    columns='File.Name',
                                                                                    values='Precursor.Normalised',
                                                                                    aggfunc=np.max)
            if piv.shape[1] == 1 or piv.shape[0] == 1:
                res = piv.max()
            else:
                piv.fillna(-1e+06, inplace=True)
                ref = piv.max()
                if piv.shape[1] >= 2:
                    #  https://github.com/vdemichev/diann-rpackage/blob/master/src/diann-rcpp.cpp 将c++代码用python复刻
                    res = maxlfq_solve(piv, margin * 1.001)
                else:
                    res = ref
                res[res <= -10] = np.nan
            result.loc[proteins[i], piv.columns] = list(res)
        r = result.applymap(np.exp)
        return r


