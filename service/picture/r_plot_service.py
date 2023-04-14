'''
对接后端进行R画图
'''
import pandas as pd

from util.Logger import logger
import os
from retrying import retry
from util.Http import HTTPPlatform


def heatmap_service(all,groups_dict,simples,result_path):
    '''
    all仅有上下调基因
    '''
    logger.debug("对接后端的R语言画热图开始")
    annotation_col_Group = []
    annotation_col_index = []
    for k,v in groups_dict.items():
        annotation_col_Group.extend([k]*len(v))
        annotation_col_index.extend(v)
    annotation_col = pd.DataFrame({"Group":annotation_col_Group},index=annotation_col_index)
    if not all.index.is_unique:
        # index有重复时
        all = all.loc[~all.index.duplicated(keep='first')]
    annotation_row = pd.DataFrame({"DEP":all["DEP"].to_list()},index=all.index)
    params = {
        "data": all.loc[:,simples].to_json(orient="columns",force_ascii=False),
        "annotation_col": annotation_col.to_json(orient="columns",force_ascii=False),
        "annotation_row": annotation_row.to_json(orient="columns",force_ascii=False)
    }
    http_platform = HTTPPlatform()
    res = http_platform.get_data_post("dfp_heatmap", params)
    if res is not None and res["code"] == 200:
        heatmap_id = res["data"]
        is_ready = if_ready(heatmap_id, http_platform)
        if is_ready:
            download(heatmap_id, http_platform, result_path)
            remove(heatmap_id, http_platform)
            logger.info("对接后端的R语言画热图完成")
            return True
    logger.info("对接后端的R语言画热图失败")
    return False


def retry_on_result_fuc(result):
    return result == False


@retry(retry_on_result=retry_on_result_fuc, stop_max_attempt_number=5, wait_fixed=50000)
def if_ready(heatmap_id, http_platform):
    '''
    数据是否分析完成
    '''
    params = {
        "heatmap_id": heatmap_id
    }
    res = http_platform.get_data("heatmap_ready", params)
    if res["code"] == 200 and res["data"]:
        return True
    else:
        return False


def download(heatmap_id,http_platform,out_dir,out_file_name="dfp_heatmap.pdf"):
    params = {
        "heatmap_id": heatmap_id,
        "file_field": "heatmap_path"
    }
    out_path = os.path.join(out_dir,out_file_name)
    http_platform.download_file("heatmap_download",params,out_path)


def remove(heatmap_id,http_platform):
    params = {
        "heatmap_id":heatmap_id
    }
    res = http_platform.get_data("heatmap_remove",params)