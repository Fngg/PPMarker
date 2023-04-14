import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score,cross_val_predict
from sklearn.metrics import confusion_matrix,precision_score, recall_score, f1_score, roc_curve,roc_auc_score
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.linear_model import SGDClassifier
from matplotlib.backends.backend_pdf import PdfPages
from config.global_config import software_name,biomarker_model_dirname
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
import os,datetime
import joblib

mpl.rc('axes', labelsize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)
plt.rc('font',family='Times New Roman')


def save_fig(image_path,fig_id, tight_layout=True, fig_extension="jpg", resolution=300):
    path = os.path.join(image_path, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)


def plot_roc_curve(fpr, tpr,auc,pdf, title=None,label=None):
    fig = plt.figure(figsize=(8, 6))  # Not shown
    ax = fig.add_subplot(111)
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')  # dashed diagonal
    plt.axis([0, 1, 0, 1])  # Not shown in the book
    plt.xlabel('False Positive Rate (Fall-Out)', fontsize=18)  # Not shown
    plt.ylabel('True Positive Rate (Recall)', fontsize=18)  # Not shown
    if title:
        plt.title(title, fontsize=20)
    # 设置刻度字体大小
    plt.text(0.7, 0.1, s="AUC = "+str(round(auc,3)), transform=ax.transAxes,fontsize=18)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.grid(True)  # Not shown
    pdf.savefig()
    plt.close()


def model_assessment_for_train(model,X,y,pdf,title=None):
    result = {}
    scores = cross_val_score(model, X, y, cv=3, scoring="accuracy")
    result["score"] = scores.mean()
    y_pred = cross_val_predict(model, X, y, cv=3)
    cm = confusion_matrix(y, y_pred)
    result["cm"] = cm.tolist()
    result["precision"] = precision_score(y, y_pred)
    result["recall"] = recall_score(y, y_pred)
    result["f1_score"] = f1_score(y, y_pred)
    if hasattr(model,"predict_proba"):
        y_probas = cross_val_predict(model, X, y, cv=3,
                                 method="predict_proba")
        y_scores = y_probas[:, 1]
    elif  hasattr(model,"decision_function"):
        y_scores = cross_val_predict(model, X, y, cv=3,
                                     method="decision_function")
    else:
        raise Exception("model 没有 'decision_function' 或 'predict_proba' 方法")
    fpr, tpr, thresholds = roc_curve(y, y_scores)

    auc = roc_auc_score(y, y_scores)
    if title:
        title = title+" in Train"
    plot_roc_curve(fpr, tpr,auc,pdf,title=title)

    result["AUC"] = auc
    return result


def model_assessment_for_test(model,X_test,y_test,pdf,dataset_type,title=None):
    result = {}
    score = model.score(X_test, y_test)
    result["score"] = score
    y_test_pred = model.predict(X_test)
    if hasattr(model,"predict_proba"):
        y_test_probas = model.predict_proba(X_test)
        y_test_scores = y_test_probas[:, 1]
    elif hasattr(model, "decision_function"):
        y_test_scores = model.decision_function(X_test)
    else:
        raise Exception("model 没有 'decision_function' 或 'predict_proba' 方法")
    cm = confusion_matrix(y_test, y_test_pred)
    result["cm"] = cm.tolist()
    result["precision"] = precision_score(y_test, y_test_pred)
    result["recall"] = recall_score(y_test, y_test_pred)
    result["f1_score"] = f1_score(y_test, y_test_pred)

    fpr, tpr, thresholds = roc_curve(y_test, y_test_scores)
    auc = roc_auc_score(y_test, y_test_scores)
    if title:
        title = title+" in "+dataset_type
    plot_roc_curve(fpr, tpr,auc,pdf,title=title)
    result["AUC"] = auc
    return result


def SGD_model(X_train_prepared, train_labels,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    sgd_clf = SGDClassifier(max_iter=1000, tol=1e-3, random_state=42)
    file_path = os.path.join(result_dir, dirname, "SGD_model_classification.pdf")
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'model classification'})
    train_result = model_assessment_for_train(sgd_clf, X_train_prepared, train_labels,pdf, title="SGDClassifier")
    sgd_clf.fit(X_train_prepared, train_labels)
    test_result = None
    if X_test_prepared is not None and test_labels is not None:
        test_result = model_assessment_for_test(sgd_clf,X_test_prepared, test_labels,pdf,"Validation", title="SGDClassifier")
    pdf.close()
    # 保存模型
    file_path = os.path.join(result_dir, dirname, "SGD_model.m")
    joblib.dump(sgd_clf, file_path)
    return train_result,test_result,sgd_clf


def naive_bayes_model(X_train_prepared, train_labels,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    clf = GaussianNB()
    file_path = os.path.join(result_dir, dirname, "naive_bayes_model_classification.pdf")
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'model classification'})
    train_result = model_assessment_for_train(clf, X_train_prepared, train_labels,pdf, title="Naive Bayes")
    clf.fit(X_train_prepared, train_labels)
    test_result = None
    if X_test_prepared is not None and test_labels is not None:
        test_result = model_assessment_for_test(clf,X_test_prepared, test_labels,pdf,"Validation", title="Naive Bayes")
    pdf.close()
    # 保存模型
    file_path = os.path.join(result_dir, dirname, "naive_bayes_model.m")
    joblib.dump(clf, file_path)
    return train_result,test_result,clf


def random_forest_model(X_train_prepared, train_labels,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    forest_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    file_path = os.path.join(result_dir, dirname, "random_forest_model_classification.pdf")
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'model classification'})
    train_result = model_assessment_for_train(forest_clf, X_train_prepared, train_labels,pdf, title="RandomForestClassifier")
    forest_clf.fit(X_train_prepared, train_labels)
    test_result = None
    if X_test_prepared is not None and test_labels is not None:
        test_result = model_assessment_for_test(forest_clf,X_test_prepared, test_labels,pdf,"Validation", title="RandomForestClassifier")
    pdf.close()
    # 保存模型
    file_path = os.path.join(result_dir, dirname, "random_forest_model.m")
    joblib.dump(forest_clf, file_path)
    return train_result,test_result,forest_clf


def svm_model(X_train_prepared, train_labels,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    svm_clf = SVC(gamma="auto", random_state=42)
    file_path = os.path.join(result_dir, dirname, "svm_model_classification.pdf")
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'model classification'})
    train_result = model_assessment_for_train(svm_clf, X_train_prepared, train_labels,pdf, title="SVM")
    svm_clf.fit(X_train_prepared, train_labels)
    test_result = None
    if X_test_prepared is not None and test_labels is not None:
        test_result = model_assessment_for_test(svm_clf,X_test_prepared, test_labels,pdf, "Validation", title="SVM")
    pdf.close()
    # 保存模型
    file_path = os.path.join(result_dir, dirname, "svm_model.m")
    joblib.dump(svm_clf, file_path)
    return train_result,test_result,svm_clf


def lr_model(X_train_prepared, train_labels,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    model = LogisticRegression()
    file_path = os.path.join(result_dir, dirname, "lr_model_classification.pdf")
    pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                        'Title': 'model classification'})
    train_result = model_assessment_for_train(model, X_train_prepared, train_labels,pdf, title="Logistic Regression")
    model.fit(X_train_prepared, train_labels)
    test_result = None
    if X_test_prepared is not None and test_labels is not None:
        test_result = model_assessment_for_test(model,X_test_prepared, test_labels,pdf, "Validation",title="Logistic Regression")
    pdf.close()
    # 保存模型
    file_path = os.path.join(result_dir, dirname, "logistic_regression_model.m")
    joblib.dump(model, file_path)
    return train_result,test_result,model


def get_english_model_name(model_name):
    # 随机森林, 非线性SVM, 朴素贝叶斯, 逻辑回归, 随机梯度下降分类
    model_name_dict = {
        "随机森林":["random_forest_model","RandomForestClassifier"],
        "非线性SVM":["svm_model","SVM"],
        "朴素贝叶斯":["naive_bayes_model","Naive Bayes"],
        "逻辑回归":["lr_model","Logistic Regression"],
        "随机梯度下降分类":["SGD_model","SGDClassifier"]
    }
    return model_name_dict[model_name]


def model_in_test(model_name,model,X_test_prepared, test_labels,result_dir,dirname=biomarker_model_dirname):
    if X_test_prepared is not None and test_labels is not None:
        model_english_name = get_english_model_name(model_name)
        file_path = os.path.join(result_dir, dirname, model_english_name[0]+"_in_test.pdf")
        pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                            'Title': 'model classification'})

        test_result = model_assessment_for_test(model, X_test_prepared, test_labels, pdf, "Validation",
                                                title=model_english_name[1])
        pdf.close()
        return test_result
    return None


def get_best_model_name(model_result_dict):
    # 根据AUC>F1分数>score>精度>召回率得到最佳的模型
    model_result_df = pd.DataFrame(model_result_dict)
    model_result_df = model_result_df.T
    for i in ["AUC","f1_score","score"]:
        max_value = model_result_df[i].max()
        model_result_df = model_result_df[model_result_df[i]==max_value]
    return model_result_df.index.tolist()