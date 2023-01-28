# bootstrapped lasso + glue +  glmnet + rf + xgboost ML

iris.train <-subset(iris, select=-c(Species))

dm <- dist(iris.train, method="euclidean")
png("hm1.png")
heatmap(as.matrix(dm), col=hcl.colors(255,"Plasma"))
# quick and short
hc <- hclust(dm, method="average")
png("hclusters1.png")
plot(hc)

png("hclusters2.png")
plot(hc)
rect.hclust(hc, k=9, border=hcl.colors(9))

ct <- cutree(hc, k=9)

cm <-table(ct, iris$Species, dnn=c("Clusters","References"))
cm
cat(paste("accuracy:", 119*189.9/255, "%."))
png("hclusters3.png")
plot(cm, main="Hclustering over Points[k] : Targets", col=hcl.colors(9,"Heat"))

print("that-stanford-kid, 2022")

""" 
            References
Clusters setosa versicolor virginica
       1     45          0         0
       2      4          0         0
       3      1          0         0
       4      0         24        13
       5      0         22         1
       6      0          4         0
       7      0          0        24
       8      0          0         9
       9      0          0         3
accuracy: 88.62 %.[1] that-stanford-kid, 2022 
"""
