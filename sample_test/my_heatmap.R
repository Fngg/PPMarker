if_sd <- function (x){
  if(is.na(sd(x)) || sd(x)==0){
    return(FALSE)
  }
  return(TRUE)
}

dfp_heatmap_plot <- function (data,annotation_col,annotation_row,targetPath){
  plotPath = file.path(targetPath,"dfp_heatmap.pdf")
  pdf(file=plotPath)

  Group=c("#F8931D","#14446A")
  names(Group)=unique(annotation_col$Group)
  DFP=c("#5c9cc0","#fb9d36")
  names(DFP)=unique(annotation_row$DFP)

  ann_colors = list(Group = Group,
                    DFP = DFP)
  col <- colorRampPalette(c("navyblue","white","darkred"))(50)
  data<-data[,apply(data, 2, if_sd)]
  pheatmap(data, color = col, cluster_row = FALSE, cluster_col = FALSE,show_rownames=FALSE,show_colnames=FALSE,annotation_col = annotation_col,border_color=NA, annotation_row = annotation_row,annotation_colors = ann_colors)

  dev.off()
}

dfp_heatmap_plot2 <- function (data,annotation_col,annotation_row,targetPath){
  plotPath = file.path(targetPath,"dfp_heatmap.pdf")
  pdf(file=plotPath)

  Group=c("#F8931D","#14446A")
  names(Group)=unique(annotation_col$Group)

  ann_colors = list(Group = Group)
  col <- colorRampPalette(c("navyblue","white","darkred"))(100)
  data<-data[,apply(data, 2, if_sd)]
  pheatmap(data, color = col, cluster_row = FALSE, cluster_col = FALSE,show_colnames=FALSE,annotation_col = annotation_col,border_color=NA,annotation_colors = ann_colors)

  dev.off()
}