from matplotlib import colors

legend_font_size = 16 # 针对图例的字体
title_font_size = 20
label_font_size = 20 # 坐标轴标题
ticks_font_size = 18

normal_figsize_size = (11.7, 8.3)
big_figsize_size = (11.7, 8.3)
small_figsize_size = (11.7, 8.3)

# 颜色设置

colorslist = ["navy","white","darkred"]
heatmap_cmaps = colors.LinearSegmentedColormap.from_list('heatmap_cmaps',colorslist,N=100)

three_color_list = ["#F8931D","#14446A","#A52A2A"]
color_list = ["#ffa500", "#2e8b57", "#8b0000", "#2366c0", "#fffb0d", "#ff9300", "#00f91a","#F8931D","#14446A","#A52A2A"]

# PCA图上点的大小
pca_dot_size = 150
