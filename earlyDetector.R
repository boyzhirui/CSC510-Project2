#calculate commits data
commits = read.csv("commits",header = FALSE)
N = dim(commits)[2]
commits_z = c(1:14)
commits_z = as.data.frame(commits_z)
for(i in 1:N)
{
  commits_z[i]=z_score(commits[[i]])
}
commits_logic = commits_z < (-0.3)
M = dim(commits)[1]
#give warning before bad smell happens
for(i in 1:M)
{
  print("================Group===============")
  print(i)
  for(j in 2:N)
  {
    if(commits_logic[i,][j]){
      if(commits_logic[i,][(j-1)]){
        print(j)
        print("Commits Early Warning: You are falling behind, you may need to put more effort")
      }
      else if(commits_z[i,][j]<(-1))
      {
        print(j)
        print("Commits Early Warning: You are falling behind, you may need to put more effort!")
      }
    }
  }
}


#calculate closed issue data
closeIssue = read.csv("IssuesClosedPerweekAllGroup.csv",header = FALSE)
N = dim(closeIssue)[2]
closeIssue_z = c(1:14)
closeIssue_z = as.data.frame(closeIssue_z)
for(i in 1:N)
{
  closeIssue_z[i]=z_score(closeIssue[[i]])
}
closeIssue_logic = closeIssue_z < (-0.3)
M = dim(closeIssue)[1]
#give warning before bad smell happens
for(i in 1:M)
{
  print("================Group===============")
  print(i)
  for(j in 2:N)
  {
    if(closeIssue_logic[i,][j]){
      if(closeIssue_logic[i,][(j-1)]){
        print(j)
        print("Closed Issues Early Warning: You are falling behind, you may need to put more effort")
      }
    }
  }
}

#calculate open issue data
openIssue = data = read.csv("IssuesOpenPerweekAllGroup.csv",header = FALSE)
N = dim(openIssue)[2]
openIssue_z = c(1:14)
openIssue_z = as.data.frame(openIssue_z)
for(i in 1:N)
{
  openIssue_z[i]=z_score(openIssue[[i]])
}
openIssue_logic = openIssue_z < (-0.3)
M = dim(openIssue)[1]
#give warning before bad smell happens
for(i in 1:M)
{
  print("================Group===============")
  print(i)
  for(j in 2:N)
  {
    if(openIssue_logic[i,][j]){
      if(commits_logic[i,][(j-1)]){
        print(j)
        print("Open Issues Early Warning: You are falling behind, you may need to put more effort")
      }
    }
  }
}


