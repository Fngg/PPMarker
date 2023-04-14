# library(glmnet)
# library(survival)
# library(survminer)
# library(survival)
# library(pheatmap)
# library(timeROC)

bioForest<-function(coxFile=null, forestFile=null){
  rt <- read.table(coxFile,header=T,sep=",",check.names=F,row.names=1)
  gene <- rownames(rt)
  hr <- sprintf("%.3f",rt$"HR")
  hrLow  <- sprintf("%.3f",rt$"HR.95L")
  hrLow[hrLow<0.001]=0.001
  hrHigh <- sprintf("%.3f",rt$"HR.95H")
  Hazard.ratio <- paste0(hr,"(",hrLow,"-",hrHigh,")")
  pVal <- ifelse(rt$pvalue<0.001, "<0.001", sprintf("%.3f", rt$pvalue))
  
  height=(nrow(rt)/15)+5
  pdf(file=forestFile, width=8, height=height)
  n <- nrow(rt)
  nRow <- n+1
  ylim <- c(1,nRow)
  layout(matrix(c(1,2),nc=2),width=c(3,2.5))
  
  xlim = c(0,3)
  par(mar=c(4,2.5,2,1))
  plot(1,xlim=xlim,ylim=ylim,type="n",axes=F,xlab="",ylab="")
  text.cex=0.8
  text(0,n:1,gene,adj=0,cex=text.cex)
  text(1.5-0.5*0.2,n:1,pVal,adj=1,cex=text.cex);text(1.5-0.5*0.2,n+1,'pvalue',cex=text.cex,adj=1)
  text(3,n:1,Hazard.ratio,adj=1,cex=text.cex);text(3,n+1,'Hazard ratio',cex=text.cex,adj=1,)
  
  par(mar=c(4,1,2,1),mgp=c(2,0.5,0))
  LOGindex=10 
  hrLow = log(as.numeric(hrLow),LOGindex)
  hrHigh = log(as.numeric(hrHigh),LOGindex)
  hr = log(as.numeric(hr),LOGindex)
  xlim = c(floor(min(hrLow,hrHigh)),ceiling(max(hrLow,hrHigh)))
  plot(1,xlim=xlim,ylim=ylim,type="n",axes=F,ylab="",xaxs="i",xlab="Hazard ratio")
  arrows(as.numeric(hrLow),n:1,as.numeric(hrHigh),n:1,angle=90,code=3,length=0.05,col="darkblue",lwd=2.5)
  abline(v=log(1,LOGindex),col="black",lty=2,lwd=2)
  boxcolor = ifelse(as.numeric(hr) > log(1,LOGindex), "red", "blue")
  points(as.numeric(hr), n:1, pch = 15, col = boxcolor, cex=1.3)
  a1 = axis(1,labels=F,tick=F)
  axis(1,a1,LOGindex^a1)
  dev.off()
}

bioSurvival=function(rt, outFile=null){
  diff=survdiff(Surv(OS, status) ~ risk, data=rt)
  pValue=1-pchisq(diff$chisq, df=1)
  if(pValue<0.001){
    pValue="p<0.001"
  }else{
    pValue=paste0("p=",sprintf("%.03f",pValue))
  }
  fit <- survfit(Surv(OS, status) ~ risk, data = rt)
  surPlot=ggsurvplot(fit, 
                     data=rt,
                     conf.int=T,
                     pval=pValue,
                     pval.size=6,
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
  pdf(file=outFile, onefile=FALSE, width=6.5, height=5.5)
  print(surPlot)
  dev.off()
}

bioRiskPlot=function(rt, riskScoreFile=null, survStatFile=null, heatmapFile=null){
  rt=rt[order(rt$riskScore),]
  
  riskClass=rt[,"risk"]
  lowLength=length(riskClass[riskClass=="low"])
  highLength=length(riskClass[riskClass=="high"])
  lowMax=max(rt$riskScore[riskClass=="low"])
  line=rt[,"riskScore"]
  line[line>10]=10
  pdf(file=riskScoreFile, width=7, height=4)
  plot(line, type="p", pch=20,
       xlab="Patients (increasing risk socre)", ylab="Risk score",
       col=c(rep("green",lowLength),rep("red",highLength)) )
  abline(h=lowMax,v=lowLength,lty=2)
  legend("topleft", c("High risk", "Low Risk"),bty="n",pch=19,col=c("red","green"),cex=1.2)
  dev.off()

  color=as.vector(rt$status)
  color[color==1]="red"
  color[color==0]="green"
  pdf(file=survStatFile, width=7, height=4)
  plot(rt$OS, pch=19,
       xlab="Patients (increasing risk socre)", ylab="Survival time (years)",
       col=color)
  legend("topleft", c("Dead", "Alive"),bty="n",pch=19,col=c("red","green"),cex=1.2)
  abline(v=lowLength,lty=2)
  dev.off()
  
  rt1=rt[!(colnames(rt) %in% c("OS","status","riskScore","risk"))]
  rt1=t(rt1)
  annotation=data.frame(type=rt["risk"])
  rownames(annotation)=rownames(rt)
  pdf(file=heatmapFile, width=7, height=4)
  pheatmap(rt1, 
           annotation=annotation, 
           cluster_cols = F,
           cluster_rows = F,
           show_colnames = F,
           scale="row",
           color = colorRampPalette(c(rep("green",5), "white", rep("red",5)))(50),
           fontsize_col=3,
           fontsize=7,
           fontsize_row=8)
  dev.off()
}

multi_cox <- function(rt,pFilter,targetPath,if_lasso){
  step_num = 1
  if(if_lasso){
    exp <- rt[,!(colnames(rt) %in% c("OS","status"))]
    x <- as.matrix(exp)
    y <- data.matrix(Surv(time = rt$OS,event = rt$status))
    set.seed(007)
    lasso_fit <- cv.glmnet(x, y, family = 'cox', type.measure = 'deviance', nfolds = 10)
    
    lambda.1se <- lasso_fit$lambda.1se
    model_lasso_1se <- glmnet(x, y, family = 'cox', type.measure = 'deviance', nfolds = 10,lambda = lambda.1se)
    gene_1se <- rownames(model_lasso_1se$beta)[as.numeric(model_lasso_1se$beta)!=0]
    if(length(gene_1se)>0){
      lasso_data_col <- c(gene_1se,c("OS","status"))
      lasso_data <- rt[,lasso_data_col]
      lasso_data2=cbind(id=row.names(lasso_data),lasso_data)
      lassocsvPath = file.path(targetPath,paste(as.character(step_num),"_lasso_result_exp.csv"))
      step_num = step_num+1
      write.table(lasso_data2,file=lassocsvPath,sep=",",row.names=F,quote=F)
      rt = lasso_data
    }else{
      rt = data.frame()
      lassocsvPath = file.path(targetPath,paste(as.character(step_num),"_lasso_result_exp.csv"))
      write.table(data.frame(),file=lassocsvPath,sep=",",row.names=F,quote=F)
    }
  }
  if(ncol(rt)>2){
    multiCox=coxph(Surv(OS, status) ~ ., data = rt)
    multiCox=step(multiCox, direction="both")
    multiCoxSum=summary(multiCox)
    
    outMultiTab=data.frame()
    outMultiTab=cbind(
      coef=multiCoxSum$coefficients[,"coef"],
      HR=multiCoxSum$conf.int[,"exp(coef)"],
      HR.95L=multiCoxSum$conf.int[,"lower .95"],
      HR.95H=multiCoxSum$conf.int[,"upper .95"],
      pvalue=multiCoxSum$coefficients[,"Pr(>|z|)"])
    rownames(outMultiTab) = rownames(multiCoxSum[["coefficients"]])
    outMultiTab2=cbind(id=row.names(outMultiTab),outMultiTab)
    
    multi_cox_csvPath = file.path(targetPath,paste(as.character(step_num),"_multiCox_result.csv"))
    step_num = step_num+1
    write.table(outMultiTab2, file=multi_cox_csvPath, sep=",",row.names=F,quote=F)
    
    multi_forest_pdfPath = file.path(targetPath,paste(as.character(step_num),"_multi_forest.pdf"))
    step_num = step_num+1
    bioForest(coxFile=multi_cox_csvPath, forestFile=multi_forest_pdfPath)
    
    score=predict(multiCox, type="risk", newdata=rt)
    coxGene=rownames(multiCoxSum$coefficients)
    coxGene=gsub("`", "", coxGene)
    outCol=c("OS", "status", coxGene)
    risk=as.vector(ifelse(score>median(score), "high", "low"))
    outTab=cbind(rt[,outCol], riskScore=as.vector(score), risk)
    risk_csvpath = file.path(targetPath,paste(as.character(step_num),"_risk.csv"))
    step_num = step_num+1
    rt_risk = outTab
    write.table(rt_risk, file=risk_csvpath, sep=",", quote=F, row.names=F)
    
    survival_pdfpath = file.path(targetPath,paste(as.character(step_num),"_survival.pdf"))
    step_num = step_num+1
    bioSurvival(rt_risk,outFile=survival_pdfpath)
    
    riskScore_pdfpath = file.path(targetPath,paste(as.character(step_num),"_riskScore.pdf"))
    step_num = step_num+1
    
    survStat_pdfpath = file.path(targetPath,paste(as.character(step_num),"_survStat.pdf"))
    step_num = step_num+1
    
    heatmap_pdfpath = file.path(targetPath,paste(as.character(step_num),"_heatmap.pdf"))
    step_num = step_num+1
    
    bioRiskPlot(rt_risk,
                riskScoreFile=riskScore_pdfpath,
                survStatFile=survStat_pdfpath,
                heatmapFile=heatmap_pdfpath)
    
    # ROC
    risk=rt_risk[,c("OS", "status", "riskScore")]
    bioCol=rainbow(3, s=0.9, v=0.9)
    
    ROC_rt=timeROC(T=risk$OS,delta=risk$status,
                   marker=risk$riskScore,cause=1,
                   weighting='aalen',
                   times=c(1,3,5),ROC=TRUE)
    roc_pdfpath = file.path(targetPath,paste(as.character(step_num),"_ROC.pdf"))
    pdf(file=roc_pdfpath, width=5, height=5)
    plot(ROC_rt,time=1,col=bioCol[1],title=FALSE,lwd=2)
    plot(ROC_rt,time=3,col=bioCol[2],add=TRUE,title=FALSE,lwd=2)
    plot(ROC_rt,time=5,col=bioCol[3],add=TRUE,title=FALSE,lwd=2)
    legend('bottomright',
           c(paste0('AUC at 1 years: ',sprintf("%.03f",ROC_rt$AUC[1])),
             paste0('AUC at 3 years: ',sprintf("%.03f",ROC_rt$AUC[2])),
             paste0('AUC at 5 years: ',sprintf("%.03f",ROC_rt$AUC[3]))),
           col=bioCol[1:3], lwd=2, bty = 'n')
    dev.off()
  }
  
}
