z_score <- function(data){
  mean_v = mean(data)
  std_v = sd(data)
  data = (data - mean(data))/std_v
  return(data)
}

data = read.csv("totalCommits.txt",header = FALSE)
test = as.matrix(data)
for(i in 1:15){
  t = as.vector(test[i,])
  t = t[!is.na(t)]
  res = z_score(t)
  print(res)
}

#paste(shQuote(res), collapse=", ")
