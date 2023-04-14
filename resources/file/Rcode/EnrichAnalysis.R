# library(org.Hs.eg.db)
# library(ggplot2)
# library(clusterProfiler)
# library(grid)

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

removeColsAllNa  <- function(x){x[, apply(x, 2, function(y) any(!is.na(y)))]}

go_analysis <- function(genes, keyType, org,targetPath){
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
  # data <- read.table(filePath, header=T, stringsAsFactor =F)
  # data <- removeColsAllNa(data)
  geneNames <- genes
  if (keyType!="ENTREZID"){
    geneNames <- bitr(geneNames, keyType, "ENTREZID", orgDb)
    geneNames <- geneNames$ENTREZID
  }
  result = enrichGO(   gene   = geneNames,
                       OrgDb  = orgDb,
                       ont   = "ALL"  ,
                       readable = TRUE)
  txtPath = file.path(targetPath,"enrich_go_result.csv")
  hh <- as.data.frame(result@result)
  write.csv (hh, file =txtPath, row.names =FALSE, col.names =TRUE)

  if (nrow(hh)>=1){
    plotPath = file.path(targetPath,"enrich_go_plots.pdf")
    report_theme<-"GoEnrich"
    pdf(plotPath,paper = "a4r",width = 11.7,height = 8.3)
    first_page(theme = "GoEnrich Report")
    page_num<-1
    ####dotplot####
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

    p1<-dotplot(result,font.size=12, split="ONTOLOGY")+facet_grid(ONTOLOGY~., scale="free")+ scale_y_discrete(labels = function(x) str_wrap(x, width = 80) )
    print(p1)

    border_plot("dotplot",page_num,report_theme)
    page_num<-page_num+1
    ####barplot####
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

    p4<-barplot(result,font.size=12, split="ONTOLOGY")+facet_grid(ONTOLOGY~., scale="free")+ scale_y_discrete(labels = function(x) str_wrap(x, width = 80) )
    print(p4)

    border_plot("barplot",page_num,report_theme)
    page_num<-page_num+1
    ####goplot####
    # layout(c(1))
    # par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
    # p2<-goplot(result, showCategory = 10)
    # print(p2)
    # border_plot("goplot",page_num,report_theme)
    # page_num<-page_num+1
    ###cnetplot###
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
    p3<-cnetplot(result,font.size=12, showCategory = 10,circular=FALSE,colorEdge = TRUE)
    print(p3)
    border_plot("cnetplot",page_num,report_theme)
    page_num<-page_num+1
    ###emapplot###
    # layout(c(1))
    # par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
    # emapplot(result, showCategory = 20)
    # border_plot("emapplot",page_num,report_theme)
    #close the pdf
    invisible(dev.off())
  }

}

kegg_analysis <- function(genes, keyType, org,targetPath){
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
  # data <- read.table(filePath, header=T, stringsAsFactor =F)
  # geneNames <- data$gene
  geneNames <- genes
  if (keyType!="ENTREZID"){
    geneNames <- bitr(geneNames, keyType, "ENTREZID", orgDb)
    geneNames <- geneNames$ENTREZID
  }
  R.utils::setOption("clusterProfiler.download.method",'auto')
  result = enrichKEGG(gene= geneNames, organism = org,pvalueCutoff =0.05,qvalueCutoff =1)

  if (!is.null(result)){
    result <- setReadable(result, orgDb, keyType = "ENTREZID")
  }


  hh <- as.data.frame(result)
  txtPath = file.path(targetPath,"enrich_kegg_result.csv")
  write.csv (hh, file =txtPath, row.names =FALSE, col.names =TRUE)

  if (nrow(hh)>=1){
    rownames(hh) <- 1:nrow(hh)
    hh$order=factor(rev(as.integer(rownames(hh))),labels = rev(hh$Description))
    # hh$Description = factor(hh$Description,levels = hh$Description,ordered = T)

    plotPath = file.path(targetPath,"enrich_kegg_plots.pdf")
    report_theme<-"KEGGEnrich"
    pdf(plotPath,paper = "a4r",width = 11.7,height = 8.3)
    first_page(theme = "KEGGEnrich Report")
    page_num<-1

    ###barplot###
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

    p1 <- ggplot(hh,aes(y=order,x=Count,fill=p.adjust))+
      geom_bar(stat = "identity",width=0.7)+
      #coord_flip()+
      scale_fill_gradient(low = "red",high ="blue" )+
      labs(title = "KEGG Pathways Enrichment",
           x = "Gene numbers",
           y = "Pathways")+
      theme(axis.title.x = element_text(face = "bold",size = 16),
            axis.title.y = element_text(face = "bold",size = 16),
            legend.title = element_text(face = "bold",size = 16))+
      theme_bw()
    print(p1)
    border_plot("barplot",page_num,report_theme)
    page_num<-page_num+1

    ###barplot###
    layout(c(1))
    par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)
    p2 <- ggplot(hh,aes(y=order,x=Count))+
      geom_point(aes(size=Count,color=-1*p.adjust))+
      scale_color_gradient(low="green",high = "red")+
      labs(color=expression(p.adjust,size="Count"),
           x="Gene Number",y="Pathways",title="KEGG Pathway Enrichment")+
      theme_bw()
    print(p2)
    border_plot("dotplot",page_num,report_theme)

    #close the pdf
    invisible(dev.off())
  }else{
    print("kegg enrich analysis no result")
  }

}
