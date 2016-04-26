one <- strptime("2016-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
two <- strptime("2016-02-01T05:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
three <- strptime("2016-03-01T05:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
four <- strptime("2016-04-01T05:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

for(i in 1:14){
  
  sum_milestones_by_month = c(0,0,0,0)
  #read raw data
  fileName = paste0("group",as.character(i),".csv", collapse = NULL)
  milestone = read.csv(fileName)
  
  #===========feature extraction==============
  #calculate total issues in each milestone
  milestone$totalIssues = milestone$open.issues+milestone$closed.issues
  
  #calculate issue z_score
  milestone$issueZscore = z_score(milestone$totalIssues)
  
  N = dim(milestone)[1]
  for(j in 1:N){
    
    createTime = strptime(as.character(milestone$created.time[j]), "%Y-%m-%dT%H:%M:%SZ")
    dueTime = strptime(as.character(milestone$due.time[j]), "%Y-%m-%dT%H:%M:%SZ")
    closeTime = strptime(as.character(milestone$closed.time), "%Y-%m-%dT%H:%M:%SZ")
    #Has opened issues after milestone closed
    if(!is.na(closeTime))
    {
      if(milestone$open.issues[j]>0)
      {
        milestone$hasOpenIssueAMC[j] <- 1
      }
      else
      {
        milestone$hasOpenIssueAMC[j] <- 0
      }
    }
    #Milestone has too few issues (1.5 or 2 std less than mean for all the milestones of this project)
    if(abs(milestone$issueZscore[j]) >= 1.5){
      milestone$abnormalIssueNumber[j] <- 1
    }
    else{
      milestone$abnormalIssueNumber[j] <- 0
    }
    
    #No due time for milestones
    if(is.na(dueTime))
    {
      milestone$noDueTime[j] <- 1
    }
    else
    {
      milestone$noDueTime[j] <- 0
    }
    # number of Milestone created in each month
    if(createTime>four){
      sum_milestones_by_month[4] = sum_milestones_by_month[4] + 1
    }
    else if(createTime>three){
      sum_milestones_by_month[3] = sum_milestones_by_month[3] + 1
    }
    else if(createTime>two){
      sum_milestones_by_month[2] = sum_milestones_by_month[2] + 1
    }
    else if(createTime>one){
      sum_milestones_by_month[1] = sum_milestones_by_month[1] + 1
    }
    
  }
  
  fileName = paste0("../processed/group",as.character(i),".csv", collapse = NULL)
  write.csv(milestone,file=fileName)
  
  fileName = paste0("../processed/group",as.character(i),"_totalInMonths.csv", collapse = NULL)
  write.csv(sum_milestones_by_month,file=fileName)
  
}