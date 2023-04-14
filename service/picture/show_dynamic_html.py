from pyecharts import options as opts
from pyecharts.charts import Scatter
from pyecharts.commons.utils import JsCode
import numpy as np
from sklearn.preprocessing import StandardScaler
from operator import itemgetter
import pandas as pd
from config.picture_config import color_list


def volcano_plot_html(result,file_path,title="",FC_threshold=1.5,pvalue_colname="Pvalue",log2fc_colname = "log2FC",dfp_colname="DEP",p_value=0.05):
    result['log(pvalue)'] = -np.log10(result[pvalue_colname])
    result["Gene names_No."] = result.index
    x_data = result[log2fc_colname]
    y_data = result.loc[:, ["log(pvalue)", "Gene names_No.", dfp_colname]]
    y_data = y_data.values.tolist()
    piece = [
        {"value": "down-regulated", 'label': 'down-regulated', 'color': 'blue'},
        {"value": "none-significant", 'label': 'none-significant', 'color': '#737373'},
        {"value": "up-regulated", 'label': 'up-regulated', 'color': '#E41A1C'}
    ]
    c = (
        Scatter()
            .add_xaxis(x_data)
            .add_yaxis(
            "",
            y_data,
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(
                formatter=JsCode(
                    """function(params){
    return params.data[2]+'<br/>'+'log2 FoldChange: '+params.data[0].toFixed(2)+'<br/>'+'-log10 pValue: '+params.data[1].toFixed(2)
    }
    """
                )
            ),
            visualmap_opts=opts.VisualMapOpts(dimension=3, is_piecewise=True, series_index=0, pieces=piece,
                                              textstyle_opts=opts.TextStyleOpts(
                                                  font_family='Times New Roman',
                                                  font_size=20,
                                              ),
                                              pos_top="center",
                                              pos_right="right"
                                              ),
            xaxis_opts=opts.AxisOpts(
                name="log2 FoldChange",
                name_location='middle',
                name_gap=20,
                #                 x轴名称的格式配置
                name_textstyle_opts=opts.TextStyleOpts(
                    font_family='Times New Roman',
                    font_size=20,
                ),
                #                 坐标轴刻度配置项
                axistick_opts=opts.AxisTickOpts(
                    #                     is_show=False,  # 是否显示
                    is_inside=True,  # 刻度线是否在内侧
                ),
                #                 坐标轴线的配置
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(
                        width=1,
                        color='black',
                    )
                ),
            ),
            yaxis_opts=opts.AxisOpts(
                name='-log10 pValue',
                name_location='middle',
                name_gap=30,
                name_textstyle_opts=opts.TextStyleOpts(
                    font_family='Times New Roman',
                    font_size=20,
                    color='black',
                    #                     font_weight='bolder',
                ),
                axistick_opts=opts.AxisTickOpts(
                    #                     is_show=False,  # 是否显示
                    is_inside=True,  # 刻度线是否在内侧
                ),
                axislabel_opts=opts.LabelOpts(
                    font_size=12,
                    font_family='Times New Roman',
                ),
            ),
            #             图例设置
            legend_opts=opts.LegendOpts(
                pos_left='right',  # 图例放置的位置，分上下左右，可用左右中表示，也可用百分比表示
                pos_top='center',
                orient='vertical',  # horizontal、vertical #图例放置的方式 横着放or竖着放
                textstyle_opts=opts.TextStyleOpts(
                    font_size=12,
                    font_family='Times New Roman',
                ),
            )
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(x=-np.log2(FC_threshold)),
                    opts.MarkLineItem(x=np.log2(FC_threshold)),
                    opts.MarkLineItem(y=-np.log10(p_value))

                ],
                # 也可以在这里设置标线两端的标记类型，可以是一个数组分别指定两端，也可以是单个统一指定，具体格式见 data.symbol。
                symbol=None,

                # 也可以在这里设置标线两端的标记大小，可以是一个数组分别指定两端，也可以是单个统一指定。
                symbol_size=None,
                # 标签配置项，参考 `series_options.LabelOpts`
                label_opts=opts.LabelOpts(),

                # 标记线样式配置项，参考 `series_options.LineStyleOpts`
                linestyle_opts=opts.LineStyleOpts(width=2, color='black', opacity=0.7, type_='dashed', )
            )
        )
            .render(file_path)
    )


def pca_plot_html(df,file_path,groups_dict,title=""):
    from sklearn.decomposition import PCA
    df = df.dropna()
    if len(df)>=2:
        df_T = df.transpose()
        # 对蛋白进行标准差标准化
        df_T_scale = StandardScaler().fit_transform(df_T)
        # 获取分组标签
        y_dict = {}
        keys = list(groups_dict.keys())
        for j in range(len(keys)):
            for k in groups_dict[keys[j]]:
                y_dict[k] = j
        y = list(itemgetter(*list(df_T.index))(y_dict))
        model = PCA(n_components=2)
        pca = model.fit_transform(df_T_scale)
        # ratio 主成分方差贡献率
        ratio = model.explained_variance_ratio_
        y1 = []
        for i in y:
            y1.append(keys[i])
        tmp = pd.DataFrame({"pca1": pca[:, 0], "pca2": pca[:, 1], "sample": df_T.index, "group": y1})
        x_data = tmp["pca1"]

        y_data = tmp.loc[:, ["pca2", "sample", "group"]]
        y_data = y_data.values.tolist()
        piece = []
        for i in range(len(keys)):
            key = keys[i]
            piece.append({"value":key,"label":key,"color":color_list[i]})
        c = (
            Scatter(init_opts=opts.InitOpts(width="700px"))
                .add_xaxis(x_data)
                .add_yaxis(
                "",
                y_data,
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode(
                        """function(params){
        return params.data[2]+'<br/>'+'PC1: '+params.data[0].toFixed(2)+'<br/>'+'PC2: '+params.data[1].toFixed(2)
        }
        """
                    )
                ),
                visualmap_opts=opts.VisualMapOpts(is_piecewise=True, series_index=0, pieces=piece,
                                                  textstyle_opts=opts.TextStyleOpts(
                                                      font_family='Times New Roman',
                                                      font_size=20,
                                                  ),
                                                  pos_top="center",
                                                  pos_right="right"
                                                  ),
                xaxis_opts=opts.AxisOpts(
                    name=f"PC1({round(ratio[0] * 100, 2)}%)",
                    name_location='middle',
                    name_gap=20,
                    #                 x轴名称的格式配置
                    name_textstyle_opts=opts.TextStyleOpts(
                        font_family='Times New Roman',
                        font_size=20,
                    ),
                    #                 坐标轴刻度配置项
                    axistick_opts=opts.AxisTickOpts(
                        #                     is_show=False,  # 是否显示
                        is_inside=True,  # 刻度线是否在内侧
                    ),
                    #                 坐标轴线的配置
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(
                            width=1,
                            color='black',
                        )
                    ),
                ),
                yaxis_opts=opts.AxisOpts(
                    name=f"PC2({round(ratio[1] * 100, 2)}%)",
                    name_location='middle',
                    name_gap=30,
                    name_textstyle_opts=opts.TextStyleOpts(
                        font_family='Times New Roman',
                        font_size=20,
                        color='black',
                        #                     font_weight='bolder',
                    ),
                    axistick_opts=opts.AxisTickOpts(
                        #                     is_show=False,  # 是否显示
                        is_inside=True,  # 刻度线是否在内侧
                    ),
                    axislabel_opts=opts.LabelOpts(
                        font_size=12,
                        font_family='Times New Roman',
                    ),
                ),

            )
                .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),

            )
                .render(file_path)
        )
