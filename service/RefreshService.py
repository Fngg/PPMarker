import util.Global as gol


### 当重新导入原始数据后，去掉gol保存的上一批数据


def refresh():
    gol.set_value("r_data_list",None)
    gol.set_value("ppndata",None)
    gol.set_value("ppndata_cutoffFilter",None)
    gol.set_value("ppndata_filter",None)
    gol.set_value("ppiData",None)
    gol.set_value("ppidata_ass",None)
