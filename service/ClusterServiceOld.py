import pandas as pd
from sklearn.cluster import KMeans
from yellowbrick.cluster.elbow import kelbow_visualizer
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import os
from util.Logger import logger
from skfuzzy import cmeans
import numpy as np
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

plt.rc('font',family='Times New Roman')


#  降维函数，方便做2D/3D图
def PCA_F(X,n):
    pca = PCA(n_components=n)
    return pca.fit_transform(X)


def fuzzy_c_means(df, target_path):
    columns = df.columns.values

    pdf_path = os.path.join(target_path, 'Fuzzy-C-Means-result.pdf')
    pdf = PdfPages(pdf_path)
    plt.figure(figsize=(11.7, 8.3))
    #  确定K值
    oz = kelbow_visualizer(KMeans(random_state=4), df, k=(2, 10), show=False)
    k = oz.elbow_value_
    pdf.savefig()
    plt.close()

    df2 = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
    center, u, u0, d, jm, p, fpc = cmeans(df2, m=2, c=k, error=0.005, maxiter=1000)


    label = np.argmax(u, axis=0)

    #  t-sne降维
    plt.figure(figsize=(11.7, 8.3))
    digits_proj = TSNE(n_components=2, perplexity=40.0,random_state=100).fit_transform(df)
    tsne_result_scaled = StandardScaler().fit_transform(digits_proj)
    cmap = mpl.colors.ListedColormap(["#FFC2CC", "#C2FFCC", "#CCC2FF", "#B0E0E6"])
    plt.scatter(tsne_result_scaled[:, 0], tsne_result_scaled[:, 1], c=label, cmap=cmap)
    plt.title("2D Clustering Result with t-sne")
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()

        # 2D或3D可视化图形
    plt.figure(figsize=(11.7, 8.3))
    cmap = mpl.colors.ListedColormap(["#FFC2CC", "#C2FFCC", "#CCC2FF", "#B0E0E6"])
    df_2D = PCA_F(df, 2)
    plt.scatter(df_2D[:, 0], df_2D[:, 1], c=label, cmap=cmap)
    plt.title("2D Clustering Result with PCA")
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()

    fig = plt.figure(figsize=(11.7, 8.3))
    ax = fig.add_subplot(projection="3d")
    df_3D = PCA_F(df, 3)
    ax.scatter(df_3D[:, 0], df_3D[:, 1], df_3D[:, 2], c=label, cmap=cmap)
    plt.title("3D Clustering Result with PCA")
    pdf.savefig()
    plt.close()



    pdf.close()

    for i in range(k):
        ci = f"C{i}"
        df[ci] = u[i, :]
    df["label"] = label
    cluster_centers = pd.DataFrame(center, columns=columns)
    xlsx_path = os.path.join(target_path, 'Fuzzy-C-Means-result.xlsx')
    with pd.ExcelWriter(xlsx_path) as writer:
        df.to_excel(writer, sheet_name='Fuzzy-C-Means-result')
        cluster_centers.to_excel(writer, sheet_name='Fuzzy-C-Means-centers')

    return True


def k_means(df,target_path):
    columns = df.columns.values

    pdf_path = os.path.join(target_path,'k-means-result.pdf')
    pdf = PdfPages(pdf_path)
    plt.figure(figsize=(11.7, 8.3))
    #  确定K值
    oz = kelbow_visualizer(KMeans(random_state=4), df, k=(2, 10), show=False)
    k = oz.elbow_value_
    logger.debug(f"聚类的k值{k}")
    pdf.savefig()
    plt.close()

    k_means = KMeans(n_clusters=k,init='k-means++',random_state=0)
    k_means.fit(df)
    k_means_result = k_means.predict(df)

    #  t-sne降维
    plt.figure(figsize=(11.7, 8.3))
    digits_proj = TSNE(n_components=2, perplexity=40.0,random_state=100).fit_transform(df)
    tsne_result_scaled = StandardScaler().fit_transform(digits_proj)
    cmap = mpl.colors.ListedColormap(["#FFC2CC", "#C2FFCC", "#CCC2FF", "#B0E0E6"])
    plt.scatter(tsne_result_scaled[:, 0], tsne_result_scaled[:, 1], c=k_means_result, cmap=cmap)
    plt.title("2D Clustering Result with t-sne")
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()

    # 2D或3D可视化图形
    plt.figure(figsize=(11.7, 8.3))
    cmap = mpl.colors.ListedColormap(["#FFC2CC", "#C2FFCC", "#CCC2FF", "#B0E0E6"])
    df_2D = PCA_F(df, 2)
    plt.scatter(df_2D[:, 0], df_2D[:, 1], c=k_means_result, cmap=cmap)
    plt.title("2D Clustering Result with pca")
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()

    fig = plt.figure(figsize=(11.7, 8.3))
    ax = fig.add_subplot(projection="3d")
    df_3D = PCA_F(df, 3)
    ax.scatter(df_3D[:, 0], df_3D[:, 1], df_3D[:, 2], c=k_means_result, cmap=cmap)
    plt.title("3D Clustering Result with pca")
    pdf.savefig()
    plt.close()

    pdf.close()

    # 输出文件
    df["label"] = k_means_result
    cluster_centers = pd.DataFrame(k_means.cluster_centers_, columns=columns)
    xlsx_path = os.path.join(target_path,'k_means_result.xlsx')
    with pd.ExcelWriter(xlsx_path) as writer:
        df.to_excel(writer, sheet_name='k-means-result')
        cluster_centers.to_excel(writer, sheet_name='k-means-cluster-centers')

    return True