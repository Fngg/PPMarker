library(survival)

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


simple_cox <- function(rt,pFilter,targetPath){
  # os is year
  outTab=data.frame()
  sigGenes=c("OS","status")
  for(gene in colnames(rt)){
    if(gene!="OS" && gene!="status"){
      cox=coxph(Surv(OS, status) ~ rt[,gene], data = rt)
      coxSummary = summary(cox)
      coxP=coxSummary$coefficients[,"Pr(>|z|)"]
      
      if(coxP<pFilter){
        sigGenes=c(sigGenes,gene)
        outTab=rbind(outTab,
                    cbind(gene=gene,
                          HR=coxSummary$conf.int[,"exp(coef)"],
                          HR.95L=coxSummary$conf.int[,"lower .95"],
                          HR.95H=coxSummary$conf.int[,"upper .95"],
                          pvalue=coxP) )
      }
    }
  }
  csvPath = file.path(targetPath,"univariable_cox.csv")
  write.table(outTab,file=csvPath,sep=",",row.names=F,quote=F)
  
  surSigExp=rt[,sigGenes]
  surSigExp=cbind(id=row.names(surSigExp),surSigExp)
  uniSigExpPath = file.path(targetPath,"univariable_exp.csv")
  write.table(surSigExp,file=uniSigExpPath,sep=",",row.names=F,quote=F)
  
  # plot
  if(nrow(outTab)<30){
    pdfPath = file.path(targetPath,"univariable_cox_forest.pdf")
    bioForest(coxFile=csvPath, forestFile=pdfPath)
  }
}

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

rt=read.table("exptime.csv", header=T, sep=",", check.names=F, row.names=1)
rt$OS=rt$OS/365
pFilter=0.05
targetPath = "."
simple_cox(rt,pFilter,targetPath)

