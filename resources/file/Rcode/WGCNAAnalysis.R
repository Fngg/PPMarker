# library(WGCNA)
# library(grid)
# options(stringsAsFactors = FALSE);
# library(stringr)

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

description_page<-function(description){
  grid::grid.newpage()
  grid::grid.text("Description:",
                  x=grid::unit(0.2, "npc"),
                  y=grid::unit(0.8, "npc"),
                  just = c("left", "top"),
                  gp=grid::gpar(fontsize=18,fontface="bold",col="black"))
  grid::grid.text(description,
                  x=grid::unit(0.2, "npc"),
                  y=grid::unit(0.7, "npc"),
                  just = c("left", "top"),
                  gp=grid::gpar(fontsize=14,col="black"))
}

preprocess  <- function(femData,datTraits,target_path){
  setwd(target_path)
    # read expression data
  # femData <- read.table(expr_csvpath, header=T, row.names= 1,sep=",")
  datExpr0 = as.data.frame(t(femData));
  #  Checking data for excessive missing values and identification of outlier microarray samples
  gsg = goodSamplesGenes(datExpr0, verbose = 3);
  if (!gsg$allOK) {
    # Optionally, print the gene and sample names that were removed:
    if (sum(!gsg$goodGenes)>0)
    printFlush(paste("Removing genes:", paste(names(datExpr0)[!gsg$goodGenes], collapse = ", ")));
    if (sum(!gsg$goodSamples)>0)
    printFlush(paste("Removing samples:", paste(rownames(datExpr0)[!gsg$goodSamples], collapse = ", ")));
    # Remove the offending genes and samples from the data:
    datExpr0 = datExpr0[gsg$goodSamples, gsg$goodGenes]
  }
  sampleTree = hclust(dist(datExpr0), method = "average");
  x <- sampleTree$height
  h <- quantile(x,probs=c(0.95))+IQR(x)*1.5
  clust = cutreeStatic(sampleTree, cutHeight = h, minSize = 10)
  outline_num = length(clust[clust==0])
  keepSamples = (clust==1)
  if(outline_num){
    outline_samples = sampleTree$labels[!keepSamples]
    subtitle = paste("Remove ",as.character(outline_num),"outliers: ",as.character(outline_samples))
    description1 = paste("After sample cluster analysis,we find ",as.character(outline_num),"outliers,which are:",as.character(outline_samples))
    print(description1)
  }else{
    subtitle = "No outliers"
    description1 = paste("After sample cluster analysis,we find no outliers")
  }
  datExpr = datExpr0[keepSamples, ]

  # traitData <- read.table(traits_csvpath, header=T,sep=",")
  samplesName = rownames(datExpr);
  # traitRows = match(samplesName, traitData[,1]);
  datTraits = datTraits[samplesName,];
  # rownames(datTraits) = traitData[traitRows, 1];

  report_theme<-""
  plotPath1 = file.path(target_path,"1_Data_input_and_cleaning.pdf")
  pdf(file=plotPath1,paper = "a4r",width = 11.7,height = 8.3)
  first_page(theme = "Sample dendrogram and trait heatmap")
  page_num<-1

  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  p1 <- plot(sampleTree, main = subtitle, sub="", xlab="", cex.lab = 1.5,
  cex.axis = 1.5, cex.main = 2)
  abline(h = h, col = "red");
  print(p1)

  border_plot("Sample dendrogram",page_num,report_theme)
  page_num<-page_num+1
   #######------------ description ------------###########
  description_page(description1)
  ########-----------Sample dendrogram without outliers and trait heatmap------------###########
  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  # Re-cluster samples
  sampleTree2 = hclust(dist(datExpr), method = "average")
  # Convert traits to a color representation: white means low, red means high, grey means missing entry
  traitColors = numbers2colors(datTraits, signed = FALSE);
  # Plot the sample dendrogram and the colors underneath.
  p2 <- plotDendroAndColors(sampleTree2, traitColors,
  groupLabels = names(datTraits),
  main = "Sample dendrogram without outliers and trait heatmap")
  print(p2)
  border_plot("Sample dendrogram and trait heatmap",page_num,report_theme)
  invisible(dev.off())

  data_list<-list("datExpr"=datExpr,
                  "datTraits"=datTraits)
  return(data_list)

}

network_construction <- function (data_list, target_path){
  setwd(target_path)
  datExpr = data_list$datExpr
  datTraits = data_list$datTraits

  powers = c(c(1:10), seq(from = 12, to=20, by=2))
  sft = pickSoftThreshold(datExpr, powerVector = powers, verbose = 5)

  # Plot the results:
  report_theme<-""
  plotPath2 = file.path(target_path,"2_Network_construction_and_module_detection.pdf")
  pdf(file=plotPath2,paper = "a4r",width = 11.7,height = 8.3)
  first_page(theme = "Network construction and module detection")
  page_num<-1

  layout(rbind(c(2), c(1)))
  par(mar=c(5, 5, 4, 5.1) + 0.1,xpd=NA)

  cex1 = 0.9;
  # Scale-free topology fit index as a function of the soft-thresholding power
  p1<-plot(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
  xlab="Soft Threshold (power)",ylab="Scale Free Topology Model Fit,signed R^2",type="n",
  main = paste("Scale independence"));
  text(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
  labels=powers,cex=cex1,col="red");
  # this line corresponds to using an R^2 cut-off of h
  abline(h=0.90,col="red")
  print(p1)

  # Mean connectivity as a function of the soft-thresholding power
  p2<-plot(sft$fitIndices[,1], sft$fitIndices[,5],
  xlab="Soft Threshold (power)",ylab="Mean Connectivity", type="n",
  main = paste("Mean connectivity"))
  text(sft$fitIndices[,1], sft$fitIndices[,5], labels=powers, cex=cex1,col="red")
  print(p2)

  border_plot("Scale Free and Mean Connectivity",page_num,report_theme)
  page_num<-page_num+1
   #######------------ description ------------###########
  description_page(paste("We choose a soft threshold of",as.character(sft$powerEstimate),"to build a scale-free network."))

  net = blockwiseModules(datExpr, power = sft$powerEstimate,
    TOMType = "unsigned", minModuleSize = 30,
    reassignThreshold = 0, mergeCutHeight = 0.25,
    numericLabels = TRUE, pamRespectsDendro = FALSE,
    saveTOMs = TRUE,
    saveTOMFileBase = "femaleMouseTOM",
    verbose = 3)

  # Convert labels to colors for plotting
  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  mergedColors = labels2colors(net$colors)
  # Plot the dendrogram and the module colors underneath
  p3 <- plotDendroAndColors(net$dendrograms[[1]], mergedColors[net$blockGenes[[1]]],
  "Module colors",
  dendroLabels = FALSE, hang = 0.03,
  addGuide = TRUE, guideHang = 0.05)
  print(p3)
  border_plot("Cluster Dendrogram",page_num,report_theme)

  invisible(dev.off())

  net_list<-list("moduleLabels"= net$colors,
                "moduleColors"=labels2colors(net$colors),
                "MEs"=net$MEs,
                "geneTree"=net$dendrograms[[1]])
  return(net_list)
}

verboseScatterplot2 <- function (topModule,module,trait,ablineH,ablineV){
  verboseScatterplot(x = topModule$Module.Membership,
                           y= topModule$Gene.significance,
                     xlab = paste("Module Membership in", module, "module"),
                     ylab = paste("Gene significance for",trait),
                     main = paste("Module membership vs. gene significance\n"),
                     cex.main = 1.2, cex.lab = 1.2, cex.axis = 1.2, col = topModule$col)
  abline(h = ablineH, v = ablineV)
}

explore_model <- function (data_list,net_list,trait,target_path){
  setwd(target_path)
  datExpr = data_list$datExpr
  datTraits = data_list$datTraits
  moduleColors = net_list$moduleColors
  nSamples = nrow(datExpr)

  # Recalculate MEs with color labels
  MEs0 = moduleEigengenes(datExpr, moduleColors)$eigengenes
  MEs = orderMEs(MEs0)
  moduleTraitCor = cor(MEs, datTraits, use = "p");
  moduleTraitPvalue = corPvalueStudent(moduleTraitCor, nSamples);

  selected_trait = datTraits[trait];
  names(selected_trait) = trait
  plotPath3 = file.path(target_path,"3_Relating_modules_to_external_clinical_traits.pdf")
  pdf(file=plotPath3,paper = "a4r",width = 12.5,height = 9)
  report_theme = paste("Relating modules to" ,trait)
  first_page(theme = paste("Relating modules to" ,trait,"and identifying important genes"))
  page_num<-1
  #######------------ the first heatmap to show all model and all traits ------------###########
  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  # Will display correlations and their p-values
  textMatrix = paste(signif(moduleTraitCor, 2), "\n(", signif(moduleTraitPvalue, 1), ")", sep = "");
  dim(textMatrix) = dim(moduleTraitCor)

  # Display the correlation values within a heatmap plot
  p1<-labeledHeatmap(Matrix = moduleTraitCor,
    xLabels = names(datTraits),
    yLabels = names(MEs),
    ySymbols = names(MEs),
    colorLabels = FALSE,
    colors = greenWhiteRed(50),
    textMatrix = textMatrix,
    setStdMargins = FALSE,
    cex.text = 0.5,
    zlim = c(-1,1),
    main = paste("Module-trait relationships"))
  print(p1)

  border_plot("correlation",page_num,report_theme)
  page_num<-page_num+1
  #######------------ description ------------###########
  description_page("The first heatmap shows the correlation between all models and all traits")
  #######------------the second cluster analysis diagram of selected traits and all model ------------###########
  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  MEs = moduleEigengenes(datExpr, moduleColors)$eigengenes
  MET = orderMEs(cbind(MEs, selected_trait))
  p2<-plotEigengeneNetworks(MET, "", marDendro = c(0,4,1,2), marHeatmap = c(3,4,1,2), cex.lab = 0.8, xLabelsAngle
                        = 90)
  print(p2)

  border_plot("correlation2",page_num,report_theme)
  page_num<-page_num+1
  #######------------ description ------------###########
  tmp1 = as.data.frame(moduleTraitCor)
  max1 = max(tmp1[trait])
  isfirstmodel = as.vector(tmp1[trait] == max1)
  firstmodel = rownames(moduleTraitCor)[isfirstmodel]

  max2 = max(tmp1[trait][!isfirstmodel,1])
  issecondmodel = as.vector(tmp1[trait] == max2)
  secondmodel = rownames(moduleTraitCor)[issecondmodel]

  description2 = paste("The second one is the cluster analysis diagram of the selected traits and \n all models.Combining the first picture and the second picture, we analyze the\n two models with the highest correlation between",trait,"and models.\n",
                      "Respectively, top1 :", firstmodel,"(cor = ",as.character(max1),")\n",
                      "top2 :", secondmodel,"(cor = ",as.character(max2),")\n")

  description_page(description2)
  #######------------The third picture shows Module membership vs. gene significance of the top1 model ------------###########
  layout(c(1))
  par(mar=c(5, 4, 4, 2) + 0.1,xpd=NA)

  modNames = substring(names(MEs), 3)
  geneModuleMembership = as.data.frame(cor(datExpr, MEs, use = "p"));
  MMPvalue = as.data.frame(corPvalueStudent(as.matrix(geneModuleMembership), nSamples));

  names(geneModuleMembership) = paste("MM", modNames, sep="");
  names(MMPvalue) = paste("p.MM", modNames, sep="");
  geneTraitSignificance = as.data.frame(cor(datExpr, selected_trait, use = "p"));
  GSPvalue = as.data.frame(corPvalueStudent(as.matrix(geneTraitSignificance), nSamples));
  names(geneTraitSignificance) = paste("GS.", names(selected_trait), sep="");
  names(GSPvalue) = paste("p.GS.", names(selected_trait), sep="");

  module = substring(firstmodel, 3)
  column = match(module, modNames);
  moduleGenes = moduleColors==module;

  topModule = data.frame("Module Membership"=abs(geneModuleMembership[moduleGenes, column]),
                          "Gene significance"=abs(geneTraitSignificance[moduleGenes, 1]),row.names =rownames(geneModuleMembership)[moduleGenes] )
  topGene = topModule[topModule[1]>=0.8&topModule[2]>=0.5,]

  ablineV = 0.8
  ablineH = 0.5
  if(nrow(topGene)==0){
    ablineV = unname(quantile(topModule$Module.Membership,0.8))
    ablineH = unname(quantile(topModule$Gene.significance,0.8))
    topGene = topModule[topModule[1]>=ablineV&topModule[2]>=ablineH,]
  }
  topModule["col"] = "brown"
  topModule["col"][rownames(topGene),] = "blue"

  p3 <- verboseScatterplot2(topModule,module,trait,ablineH,ablineV)

  print(p3)

  hubgenesFileName = paste0("hubgenesIn",str_to_title(module),".csv")
  hubgenesFileNamePath = file.path(target_path,hubgenesFileName)
  write.csv(topGene[,1:2], file = hubgenesFileNamePath )

  border_plot("Module membership vs gene significance",page_num,report_theme)
  page_num<-page_num+1
  #######------------ description ------------###########
  description_page(paste("The third picture shows that the correlation between genes andmodule is\n related to the correlation between genes and traits.This shows that important\n genes in modules that are highly related to traits are also more related to\n traits. So we only need to explore the important genes in the module.The \n hubgenes output is in",hubgenesFileName))
  #######------------ output the gene info file ------------###########

  geneInfo0 = data.frame(geneName = names(datExpr),
                         moduleColor = moduleColors,
                         geneTraitSignificance,
                         GSPvalue)
  modOrder = order(-abs(cor(MEs, selected_trait, use = "p")));
  # Add module membership information in the chosen order
  for (mod in 1:ncol(geneModuleMembership))
  {
    oldNames = names(geneInfo0)
    geneInfo0 = data.frame(geneInfo0, geneModuleMembership[, modOrder[mod]],
                           MMPvalue[, modOrder[mod]]);
    names(geneInfo0) = c(oldNames, paste("MM.", modNames[modOrder[mod]], sep=""),
                         paste("p.MM.", modNames[modOrder[mod]], sep=""))
  }
  # Order the genes in the geneInfo variable first by module color, then by geneTraitSignificance
  geneOrder = order(geneInfo0$moduleColor, -abs(geneInfo0[paste("GS.",trait,sep = "")]));
  geneInfo = geneInfo0[geneOrder, ]
  geneInfoPath = file.path(target_path,"geneInfo.csv")
  write.csv(geneInfo, file =geneInfoPath ,row.names = FALSE)

  description_page(paste("Output the correlation value and P value of the selected traits and genes, all\n modules in ",target_path,"/geneInfo.csv",sep=""))
  invisible(dev.off())

}

wgcna_analysis <- function(femData,datTraits,target_path,trait){
  data_list = preprocess(femData,datTraits,target_path)
  net_list = network_construction(data_list,target_path)
  explore_model(data_list,net_list,trait,target_path)
}

# target_path = "C://Users//aohan//Documents//R_projects//wgcna"
# expr_csvpath = "C://Users//aohan//Documents//R_projects//wgcna/data.csv"
# traits_csvpath = "C://Users//aohan//Documents//R_projects//wgcna/trait.csv"
# trait = "weight_g"
# femData = read.table(expr_csvpath, header=T, row.names= 1,sep=",")
# datTraits = read.table(traits_csvpath, header=T, row.names= 1,sep=",")
# wgcna_analysis(femData,datTraits,target_path,trait)



