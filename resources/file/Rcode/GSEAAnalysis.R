# library(org.Hs.eg.db)
# library(ggplot2)
# library(clusterProfiler)
# library(grid)
# library(enrichplot)
# library(dplyr)
# library(data.table)


change_gene <- function(data,keyType){
  if (keyType!="ENTREZID"){
    gene <- data[,keyType]
    gene=bitr(gene,fromType=keyType,toType="ENTREZID",OrgDb="org.Hs.eg.db") 
    if (keyType=="SYMBOL"){
      gene <- dplyr::distinct(gene,SYMBOL,.keep_all=TRUE)
    }else{
      gene <- dplyr::distinct(gene,ENTREZID,.keep_all=TRUE)
    }
    data_all <- data %>% 
      inner_join(gene,by=keyType)
  }else{
    data_all <- data
  }
  data_all <- data_all[order(data_all$logFC,decreasing=TRUE),]
  FCgenelist <- data_all$logFC
  names(FCgenelist) <- data_all$ENTREZID
  return(FCgenelist)
}

border_plot<-function(figure_theme,page_number,report_theme){
  grid::grid.text(figure_theme,
                  x=grid::unit(c(0.12), "npc"),
                  y=grid::unit(c(0.99), "npc"),
                  gp=grid::gpar(col="black",fontsize=12))
  grid::grid.text(report_theme,
                  x=grid::unit(c(0.90), "npc"),
                  y=grid::unit(c(0.99), "npc"),
                  gp=grid::gpar(col="black",fontsize=12))
  grid::grid.text(paste0("page ",page_number),
                  x=grid::unit(c(0.9), "npc"),
                  y=grid::unit(c(0.01), "npc"),
                  gp=grid::gpar(col="navyblue",fontsize=8))
}

first_page<-function(theme){
  ####set first page####
  grid::grid.newpage()
  grid::grid.text(theme,
                  y=grid::unit(0.6, "npc"),
                  gp=grid::gpar(fontsize=24,fontface="bold",col="black"))
  grid::grid.text(paste0("Created on: ",Sys.time()),
                  y=grid::unit(0.35, "npc"),
                  gp=grid::gpar(fontsize=18,col="navyblue"))
  
}

gsea_go_analysis <- function(data, enrichGeneType, org,targetPath){
  data <- change_gene(data,enrichGeneType)
  if(org!="hsa" & org!="mmu"){
    print("Species only support humans for the time being")
  }
  if(org=="hsa"){
    library(org.Hs.eg.db)
    orgDb = org.Hs.eg.db
  }else{
    library(org.Mm.eg.db)
    orgDb = org.Mm.eg.db
  }
  resultGO_MF = gseGO(   geneList     =  data,
                       OrgDb  = orgDb,
                       ont   = "MF"  ,pvalueCutoff = 0.05,  pAdjustMethod = "BH")
  resultGO_MF <- setReadable(resultGO_MF, orgDb, keyType = "ENTREZID")
  hh_MF <- as.data.frame(resultGO_MF)
  hh_MF$ONTOLOGY <- resultGO_MF@setType
  resultGO_BP = gseGO(   geneList     =  data,
                         OrgDb  = orgDb,
                         ont   = "BP"  ,pvalueCutoff = 0.05,  pAdjustMethod = "BH")
  resultGO_BP <- setReadable(resultGO_BP, orgDb, keyType = "ENTREZID")
  hh_BP <- as.data.frame(resultGO_BP)
  hh_BP$ONTOLOGY <- resultGO_BP@setType
  resultGO_CC = gseGO(   geneList     =  data,
                         OrgDb  = orgDb,
                         ont   = "CC"  ,pvalueCutoff = 0.05,  pAdjustMethod = "BH")
  resultGO_CC <- setReadable(resultGO_CC, orgDb, keyType = "ENTREZID")
  hh_CC <- as.data.frame(resultGO_CC)
  hh_CC$ONTOLOGY <- resultGO_CC@setType
  txtPath = file.path(targetPath,"GSEA_GO_result.csv")
  hh = list(hh_CC,hh_BP,hh_MF)
  hh = rbindlist(hh, use.names=TRUE)
  write.csv (hh, file =txtPath, row.names =FALSE, col.names =TRUE)
  
  if (nrow(hh)>=1){
    plotPath = file.path(targetPath,"GSEA_GO_plots.pdf")
    report_theme<-"GSEAGoEnrich"
    pdf(plotPath,paper = "a4r",width = 11.7,height = 8.3)
    first_page(theme = "GSEA Go Enrich Report")
    page_num<-1
    ####dotplot####
    if (nrow(hh_CC)>=1){
      layout(c(1))
      par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
      
      p1<-dotplot(resultGO_CC,font.size=12, split=".sign")+facet_grid(~.sign)
      print(p1)
      
      border_plot("Cellular Component",page_num,report_theme)
      page_num<-page_num+1
      
      top_num <- 10
      if (nrow(hh_CC)<10){
        top_num <- nrow(hh_CC)
      }
      hh_CC <- hh_CC[order(hh_CC$pvalue,decreasing=FALSE),]
      for (i in 1:top_num){
        layout(c(1))
        par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
        
        pathway.id = hh_CC[i,"ID"]
        pgsea <- gseaplot2(resultGO_CC, 
                  color = "red",
                  geneSetID = pathway.id,
                  pvalue_table = T)
        print(pgsea)
        
        border_plot("Cellular Component",page_num,report_theme)
        page_num<-page_num+1
      }
    }
    ###
    if (nrow(hh_MF)>=1){
      layout(c(1))
      
      par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
      
      p12<-dotplot(resultGO_MF,font.size=12, split=".sign")+facet_grid(~.sign)
      print(p12)
      
      border_plot("Molecular Function",page_num,report_theme)
      page_num<-page_num+1
      
      top_num <- 10
      if (nrow(hh_MF)<10){
        top_num <- nrow(hh_MF)
      }
      hh_MF <- hh_MF[order(hh_MF$pvalue,decreasing=FALSE),]
      for (i in 1:top_num){
        layout(c(1))
        par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
        
        pathway.id = hh_MF[i,"ID"]
        pgsea <- gseaplot2(resultGO_MF, 
                           color = "red",
                           geneSetID = pathway.id,
                           pvalue_table = T)
        print(pgsea)
        
        border_plot("Molecular Function",page_num,report_theme)
        page_num<-page_num+1
      }
    }
    
    ###
    if (nrow(hh_BP)>=1){
      layout(c(1))
      par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
      
      p13<-dotplot(resultGO_BP,font.size=12, split=".sign")+facet_grid(~.sign)
      print(p13)
      
      border_plot("Biological Process",page_num,report_theme)
      page_num<-page_num+1
      
      top_num <- 10
      if (nrow(hh_BP)<10){
        top_num <- nrow(hh_BP)
      }
      hh_BP <- hh_BP[order(hh_BP$pvalue,decreasing=FALSE),]
      for (i in 1:top_num){
        layout(c(1))
        par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
        
        pathway.id = hh_BP[i,"ID"]
        pgsea <- gseaplot2(resultGO_BP, 
                           color = "red",
                           geneSetID = pathway.id,
                           pvalue_table = T)
        print(pgsea)
        
        border_plot("Biological Process",page_num,report_theme)
        page_num<-page_num+1
      }
    }
    ####
    invisible(dev.off())
  }
  
}

gsea_kegg_analysis <- function(data, enrichGeneType, org,targetPath){
  data <- change_gene(data,enrichGeneType)
  if(org!="hsa" & org!="mmu"){
    print("Species only support humans for the time being")
  }
  if(org=="hsa"){
    library(org.Hs.eg.db)
    orgDb = org.Hs.eg.db
  }else{
    library(org.Mm.eg.db)
    orgDb = org.Mm.eg.db
  }
  gseaKEGG <- gseKEGG(geneList     = data,organism     = org,
                      minGSSize    = 10,pvalueCutoff = 0.05,verbose      = TRUE)

  result <- setReadable(gseaKEGG, orgDb, keyType = "ENTREZID")
  hh <- as.data.frame(result)
  txtPath = file.path(targetPath,"GSEA_KEGG_result.csv")
  write.csv (hh, file =txtPath, row.names =FALSE, col.names =TRUE)
  
  if (nrow(hh)>=1){
    plotPath = file.path(targetPath,"GSEA_KEGG_plots.pdf")
    report_theme<-"GSEAKEGGEnrich"
    pdf(plotPath,paper = "a4r",width = 11.7,height = 8.3)
    first_page(theme = "GSEAKEGG Enrich Report")
    page_num<-1
    ####dotplot####
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
    
    p1<-dotplot(gseaKEGG,font.size=12,showCategory=10,split=".sign")+facet_grid(~.sign)
    print(p1)
    
    border_plot("GSEA_KEGG",page_num,report_theme)
    page_num<-page_num+1
    
    top_num <- 10
    if (nrow(hh)<10){
      top_num <- nrow(hh)
    }
    hh <- hh[order(hh$pvalue,decreasing=FALSE),]
    for (i in 1:top_num){
      layout(c(1))
      par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
      
      pathway.id = hh[i,"ID"]
      pgsea <- gseaplot2(result, 
                         color = "red",
                         geneSetID = pathway.id,
                         pvalue_table = T)
      print(pgsea)
      
      border_plot("GSEA_KEGG",page_num,report_theme)
      page_num<-page_num+1
    }
    ####
    invisible(dev.off())
  }
  
}


