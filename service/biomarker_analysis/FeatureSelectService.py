import pandas as pd
from sklearn.linear_model import Ridge, Lasso,LogisticRegression
from sklearn.linear_model import LassoCV,RidgeCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE,RFECV
from sklearn.model_selection import GridSearchCV

from util.Logger import logger
import numpy as np

from service.picture.show_data_cluster import draw_pca_cluster
from service.picture.show_dfps import dfps_scatterplot, dfps_heatmap
import math


def rank_to_dict(ranks, names, order=1,scaler =True):
    if scaler:
        minmax = MinMaxScaler()
        ranks = minmax.fit_transform(order * np.array([ranks]).T).T[0]
        ranks = map(lambda x: round(x, 2), ranks)
    return dict(zip(names, ranks))


def l1(X, y,names,neg_indexs,pos_indexs,boostrap=False,frequencys=1000):
    alphas = 10 ** np.linspace(-2, 3, 300)  # 参数范围
    lasso_cv = LassoCV(alphas=alphas, cv=10).fit(X, y)
    alpha = lasso_cv.alpha_

    # lasso_cv = LassoCV(n_alphas=300,cv=10).fit(X, y)
    # alpha = lasso_cv.alpha_
    logger.info(f"lasso特征筛选算法选择的学习率为:{alpha}")

    # 当学习率太小时需要提高迭代次数???
    # 自主抽样1000次，有放回的抽样+分层抽样
    total_coef = lasso_cv.coef_
    if boostrap:
        y = np.array(y)
        for frequency in range(frequencys):
            np.random.seed(frequency)
            # 1000次貌似要跑一个小时，跑100次
            neg_choice_index = np.random.choice(neg_indexs, size=len(neg_indexs), replace=True)
            pos_choice_index = np.random.choice(pos_indexs, size=len(pos_indexs), replace=True)
            choice_indexs = np.concatenate([neg_choice_index, pos_choice_index])
            y_choice = y[choice_indexs]
            X_choice = X.iloc[choice_indexs]
            if frequency%50==0:
                logger.debug(f"lasso 自主抽样第{frequency},choice_indexs:{choice_indexs}")

            lasso = Lasso(alpha=alpha,max_iter=1000)
            lasso.fit(X_choice, y_choice)
            total_coef = total_coef+lasso.coef_

    ## 或者采用lasso-逻辑回归
    # https://blog.csdn.net/gracejpw/article/details/102542510
    # lr = LogisticRegression(penalty="l1",solver="liblinear",C=0.05,max_iter=1000)
    # lr = lr.fit(X,y)
    # total_coef2 = lr.coef_[0]

    # return rank_to_dict(np.abs(total_coef), names,scaler=False)
    return  dict(zip(names, np.abs(total_coef)))


def l2(X, y,names):
    alphas = 10 ** np.linspace(-5, 10, 500)  # 参数范围
    rd_cv = RidgeCV(alphas=alphas, cv=10, scoring='r2').fit(X, y)
    alpha = rd_cv.alpha_
    logger.debug(f"最佳的Ridge岭回归正则化参数是：{alpha}")
    # ridge = Ridge(alpha=7)
    # ridge.fit(X, y)
    # return rank_to_dict(np.abs(rd_cv.coef_), names)
    return  dict(zip(names, np.abs(rd_cv.coef_)))


def rf(X, y,names):
    # sklearn中的神器:GridSearcherCV(),它使用交叉验证的方式,对某一分类器,你制定想要调参的名称和数值,作为一个字典传入进这个函数,然后它就会告诉你最佳的参数组合.(其实就是for for for都试试).
    param_test1 = {"n_estimators": range(1000, 2000, 100)}
    gsearch1 = GridSearchCV(estimator=RandomForestClassifier(), param_grid=param_test1,
                            scoring='roc_auc', cv=5)
    gsearch1.fit(X,y)
    n_estimators = gsearch1.best_params_["n_estimators"]
    logger.info(f"随机森林选择的最佳树的数目为：{n_estimators}")
    rf = RandomForestClassifier(n_estimators=n_estimators)
    rf.fit(X, y)
    # return rank_to_dict(rf.feature_importances_, names)
    return dict(zip(names, rf.feature_importances_))


def ref_select(X, y,names,n_features_to_select=None):
    # 递归特征消除法
    # if n_features_to_select is None:
    #     n_features_to_select = math.ceil(len(y)/10)
    # selector = RFE(RandomForestClassifier(n_estimators=500), n_features_to_select=n_features_to_select, step=20).fit(X, y) # n_features_to_select表示筛选最终特征数量，step表示每次排除一个特征
    # importance = selector.support_+0 # 将ture、false转为1，0
    #  交叉验证递归特征消除法
    selector = RFECV(RandomForestClassifier(n_estimators=500), cv=10, step=5)
    selector = selector.fit(X, y)
    importance = selector.support_+0 # 将ture、false转为1，0
    logger.info(f"交叉验证递归特征消除法选择最优的特征数量是：{selector.n_features_}")

    return dict(zip(names, importance))


def feature_select(X,y,names,max_feature_num,method="lasso"):
    '''
    X为行为样本，列为特征的矩阵，y为一维矩阵，names为特征名称
    # https: // zhuanlan.zhihu.com / p / 141704199
    '''
    neg_indexs = [i for i in range(len(y)) if y[i]==0]
    pos_indexs = [i for i in range(len(y)) if y[i]==1]
    ranks = {}
    if method == "lasso":
        ranks["lasso"] = l1(X, y,names,neg_indexs,pos_indexs,boostrap=False,frequencys=1000)
    elif method == "l2":
        # 当样本数量特别多时使用岭回归来特征选择
        ranks["l2"] = l2(X, y, names)
    elif method=="RF":
        ranks["RF"] = rf(X, y,names)
    elif method=="RFE":
        ranks["RFE"] = ref_select(X, y,names,n_features_to_select = max_feature_num)
    else:
        logger.error(f"传入的特征筛选方法不存在，method:{method}")
    df = pd.DataFrame(ranks)
    df = df.sort_values(by=df.columns[0], axis=0,ascending=False)
    return df


def difference_analysis_plot(all,FC_threshold,groups,simples,groups_dict,pdf,pvalue_colname="Pvalue",log2fc_colname = "log2FC",dfp_colname="DEP",p_value=0.05,dir_path=None):
    # 差异蛋白火山图
    dfps_scatterplot(all, pdf, FC_threshold=FC_threshold, pvalue_colname=pvalue_colname, log2fc_colname=log2fc_colname,
                     dfp_colname=dfp_colname,p_value=p_value,dir_path=dir_path)
    dfp_index = all.loc[all[dfp_colname] != "none-significant", :].index
    draw_pca_cluster(all.loc[dfp_index, simples], groups_dict, "Differential Proteins", pdf,dir_path=dir_path)
    tmp = simples.copy()
    tmp.append(dfp_colname)
    df3 = all.loc[dfp_index, tmp].copy()
    def sub_fuc(row):
        name = row.name
        if isinstance(name,str):
            if len(name) > 25:
                return name.split("_")[-1]
        else:
            logger.warning("蛋白名称类型异常："+str(name))
        return name
    df3.index = df3.apply(lambda row: sub_fuc(row), axis=1)
    df3.sort_values(by=dfp_colname, inplace=True, ascending=True)
    dfps_heatmap(df3, groups, pdf,title="Difference Analysis",dir_path=dir_path)


def get_top_features(col_series,top_features_num):
    positive_series = col_series[col_series > 0]
    if len(positive_series)>top_features_num:
        return positive_series[0:top_features_num].index.tolist()
    else:
        return positive_series.index.tolist()


def feature_select_plot(feature_select_result,ori_data,groups_dict,groups,pdf,top_features_num = 200,dir_path=None):
    for col_name, col in feature_select_result.iteritems():
        # 按照列来检索
        # 取前200个重要的特征,并且特征的重要性评分大于0
        feature_names = get_top_features(col,top_features_num)
        data = ori_data.loc[feature_names, :].copy()
        if len(feature_names)>=2:
            draw_pca_cluster(data, groups_dict, col_name, pdf,dir_path=dir_path)

        def sub_fuc(row):
            name = row.name
            if isinstance(name,str) and len(name) > 25:
                return name.split("_")[-1]
            return name
        data.index = data.apply(lambda row: sub_fuc(row), axis=1)
        if len(feature_names) >= 2:
            dfps_heatmap(data, groups, pdf,row_cluster=True,title=col_name)
        else:
            dfps_heatmap(data, groups, pdf, row_cluster=False, title=col_name)


def get_final_features(df,max_feature_num,feature_fuc_name):
    col = df[feature_fuc_name]
    feature_names = get_top_features(col, max_feature_num)
    if "DEP" in df.columns:
        final_features_df = df.loc[(df.index.isin(feature_names)) & (df["DEP"] != "none-significant"),feature_fuc_name].to_frame()
    else:
        final_features_df = df.loc[df.index.isin(feature_names),feature_fuc_name].to_frame()
    return final_features_df,final_features_df.index.tolist()


def get_final_features_feqi(df,max_feature_num,pgroup,ngroup,feature_fuc_name,difference_analysis=True):
    final_features_dict = {}
    for col_name, col in df.iteritems():
        if col_name in [pgroup+"_mean",ngroup+"_mean","Pvalue","log2FC","FoldChange(FC)","DEP"]:
            continue
        feature_names = get_top_features(col, max_feature_num)
        if difference_analysis:
            final_features_dict[col_name] =df[(df.index.isin(feature_names)) & (df["DEP"]!="none-significant")].index.tolist()
        else:
            final_features_dict[col_name] = feature_names
    # 取交集
    final_features_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in final_features_dict.items()]))
    final_features_list=  list(final_features_dict.values())
    if len(final_features_list)>=2:
        l = []
        for i in range(1,len(final_features_list)):
            l.append(f"final_features_list[{i}]")
        s = f"list(set(final_features_list[0]).union({','.join(l)}))"
        final_features = eval(s)
        return final_features_df,final_features
    elif len(final_features_list)==1:
        return final_features_df,final_features_list[0]
    else:
        return final_features_df,[]







