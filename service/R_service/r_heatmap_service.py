import pandas as pd
from rpy2 import robjects
from rpy2.robjects import pandas2ri
pandas2ri.activate()
import numpy as np
import util.Global as gol
import os
from service.R_service.common_service import check_can_use_R


def draw_r_heatmap_service(all,groups_dict,simples,result_path):
    check_can_use_R()
    annotation_col_Group = []
    annotation_col_index = []
    for k,v in groups_dict.items():
        annotation_col_Group.extend([k]*len(v))
        annotation_col_index.extend(v)
    annotation_col = pd.DataFrame({"Group":annotation_col_Group},index=annotation_col_index)
    if not all.index.is_unique:
        # index有重复时
        all = all.loc[~all.index.duplicated(keep='first')]
    all.sort_values(by="DEP", ascending=True,inplace=True)
    annotation_row = pd.DataFrame({"DEP":all["DEP"].to_list()},index=all.index)
    robjects.r('''
               library(pheatmap)
            ''')
    r_data = pandas2ri.py2rpy( all.loc[:,simples].applymap(lambda x: np.log2(x+1)))
    r_annotation_col = pandas2ri.py2rpy(annotation_col)
    r_annotation_row = pandas2ri.py2rpy(annotation_row)
    rsource = robjects.r("source")
    ResourcePath = gol.get_value("ResourcePath")
    codePath = os.path.join(ResourcePath, "file","Rcode", "my_heatmap.R")
    rsource(codePath, encoding="utf-8")
    dfp_heatmap_plot = robjects.r("dfp_heatmap_plot")
    dfp_heatmap_plot(r_data, r_annotation_col, r_annotation_row, result_path)
    return True