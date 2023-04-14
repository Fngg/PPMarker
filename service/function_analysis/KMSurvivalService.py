import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
from lifelines.statistics import logrank_test
from matplotlib.backends.backend_pdf import PdfPages
from config.global_config import software_name, save_png
import os,datetime

plt.rc('font',family='Times New Roman')

def get_median_col(v,median_v):
    if v>=median_v:
        return "high"
    elif v< median_v:
        return "low"
    else:
        return "low"

def km_survival(data,feature,survival_time,survival_status,result_path,bi=False):
    # bi表示是否是二分类变量
    if bi and len(data[feature].unique())==2:
        label1 = data[feature].unique()[0]
        label2 = data[feature].unique()[1]
        T = data[survival_time]
        E = data[survival_status]
        high = (data[feature] == label1)
        results = logrank_test(T[high], T[~high], event_observed_A=E[high], event_observed_B=E[~high])
        logrank_p = results.p_value
    else:
        m = data[feature].median()
        data['group'] = data.apply(lambda x: get_median_col(x[feature], m), axis=1)
        T = data[survival_time]
        E = data[survival_status]
        high = (data['group'] == 'high')
        results = logrank_test(T[high], T[~high], event_observed_A=E[high], event_observed_B=E[~high])
        logrank_p = results.p_value
        label1 = "High expression"
        label2 = "Low expression"

    if logrank_p < 0.05:
        file_path = os.path.join(result_path, "survival_plot", feature + ".pdf")
        pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                            'Title': 'model classification'})

        # fig = plt.figure(figsize=(8, 8))  # Not shown

        ax = plt.subplot(111)
        kmf = KaplanMeierFitter()
        kmf.fit(T[high], event_observed=E[high], label=label1)
        kmf.plot(ax=ax, ci_show=False)
        kme = KaplanMeierFitter()
        kme.fit(T[~high], event_observed=E[~high], label=label2)
        kme.plot(ax=ax, ci_show=False)
        title = "%s ( p = %.2e )" % (feature, logrank_p)
        ax.set_title(title)
        plt.ylabel("Survival probability")
        add_at_risk_counts(kmf, kme, ax=ax)
        plt.tight_layout()
        # plt.xlabel("Survival Time (days)")
        pdf.savefig()
        if save_png:
            png_path = os.path.join(result_path, "survival_plot", feature + ".png")
            plt.savefig(png_path, dpi=300)
        plt.close()
        pdf.close()
    return logrank_p