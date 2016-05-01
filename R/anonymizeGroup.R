milestone = read.csv("milestones.csv")
for(i in 1:14){
  index = unique(milestone$group)[i]
  g = milestone[milestone$group == index,]
  g$group <- NULL
  fileName = paste0("./Data/milestones/raw/group",as.character(i),".csv", collapse = NULL)
  write.csv(g,file=fileName,row.names = FALSE)
}
