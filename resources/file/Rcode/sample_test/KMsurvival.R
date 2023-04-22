library(survival)
library(survminer)

## 读取 需要进行生存分析的基因来进行筛选
exp_data <- read.csv("C://Users//aohan//Project//iris//flow-gui//test//km_survival//unicox_example_data.csv",row.names = 1,header = T)


## 批量计算

mySurv=with(exp_data,Surv(OS, status))
log_rank_p <- lapply(tartget_genes[,"gene"] , function(g){
  g = "STEAP3.AS1"
  # 注意：需要去判断感兴趣的基因是否在表达矩阵中，存在于表达矩阵的基因才可以做生存分析

  exp_data$group=ifelse(as.numeric(exp_data[,g])>median(as.numeric(exp_data[,g])),'high','low')
  data.survdiff=survdiff(mySurv~group,data=exp_data)
  p.val = 1 - pchisq(data.survdiff$chisq, length(data.survdiff$n) - 1)
  return(p.val)

})
table(log_rank_p<0.01)
table(log_rank_p<0.001)

log_rank_p_df<- data.frame("log_rank_p" =log_rank_p)
colnames(log_rank_p_df) = tartget_genes[,"gene"]
rownames(log_rank_p_df) = "log_rank_p"
log_rank_p_df<- data.frame(t(log_rank_p_df))
write.csv(log_rank_p_df,"tartget_gene_logrankp.csv")

# 生成单个基因的生存分析图
if(!dir.exists("survival_plot"))dir.create("survival_plot")
for (g in tartget_genes[log_rank_p_df["log_rank_p"]<0.01]) {
  if (g %in% rownames(exp_data)){
    filename = paste0("survival_plot/",g, ".pdf")
    clinial_data$gene=ifelse(as.numeric(exp_data[g,])>median(as.numeric(exp_data[g,])),'high','low')
    sfit1=survfit(Surv(time, Status)~gene, data=clinial_data)
    #绘制生存曲线
    pdf(file=filename, onefile=FALSE, width=6.5, height=5.5)
    surPlot=ggsurvplot(sfit1, 
                       data=clinial_data,
                       conf.int=T,
                       pval = TRUE, # 添加P值
                       pval.size=5,
                       surv.median.line = "hv",
                       legend.title="Risk",
                       legend.labs=c("High risk", "Low risk"),
                       xlab="Time(years)",
                       break.time.by = 1,
                       palette=c("red", "blue"),
                       risk.table=TRUE,
                       risk.table.title="",
                       risk.table.col = "strata",
                       risk.table.height=.25)
    print(surPlot)
    dev.off()
  }
}

