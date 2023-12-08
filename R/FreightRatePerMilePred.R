---
title: "Freight 3PL Algorithmic Design"
author: "Patrick ONeil"
date: "12/01/2022"
output:
  pdf_document: default
  html_document: default
editor_options:
  chunk_output_type: console
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)

require(openxlsx)
require(lubridate)
require(reshape2)
require(rms)
require(Hmisc)
require(tidyverse)
require(kableExtra)
require(glmnet)
require(stringr)
dat <- read.csv("freight proj.csv", header = TRUE)
d1 <- dat[, 1:22]
d2 <- dat[, 23:36]
d3 <- dat[, 37:56]
```

## d1

```{r, echo=FALSE, results=FALSE}
d1 <- dat[, 1:22]
d1 <- d1[complete.cases(d1), ]
d1$Year <- as.factor(d1$Year)
d1$Month <- as.factor(d1$Month)
d1$Month.1 <- NULL
d1$Miles.Per.Gallon.Both.Truck <- NULL
d1$Date <- NULL
names(d1)[3] <- "Actual.Fuel"
names(d1)[4] <- "Est.Fuel.Van"
names(d1)[5] <- "Est.Fuel.Reef"
names(d1)[8] <- "Acutal.Rate.Reef.NoFuel"
names(d1)[9] <- "Acutal.Rate.Reef.Fuel"
names(d1)[10] <- "Acutal.Rate.Reef.NoFuel.LOW"
names(d1)[11] <- "Fuel.Reef"
names(d1)[13] <- "Reef.PerTrip"
names(d1)[14] <- "Acutal.Rate.Van.NoFuel"
names(d1)[15] <- "Acutal.Rate.Van.Fuel"
names(d1)[17] <- "Fuel.Van"
names(d1)[18] <- "Van.PerTrip"
d1$Reef.Rate.Fuel.RangeLow <- substring(d1$Reef.Range.Rate.Including.Fuel, 1, 4)
d1$Reef.Rate.Fuel.RangeHigh <- substring(d1$Reef.Range.Rate.Including.Fuel, 6, 9)
d1$Van.Rate.Fuel.RangeLow <- substring(d1$Van.Rate.Range.Including.Fuel, 1, 4)
d1$Van.Rate.Fuel.RangeHigh <- substring(d1$Van.Rate.Range.Including.Fuel, 6, 9)
d1$Van.Rate.Range.Including.Fuel <- NULL
d1$Reef.Range.Rate.Including.Fuel <- NULL
d1$Van.Rate.Fuel.RangeHigh <- as.numeric(d1$Van.Rate.Fuel.RangeHigh)
d1$Van.Rate.Fuel.RangeLow <- as.numeric(d1$Van.Rate.Fuel.RangeLow)
d1$Reef.Rate.Fuel.RangeHigh <- as.numeric(d1$Reef.Rate.Fuel.RangeHigh)
d1$Reef.Rate.Fuel.RangeLow <- as.numeric(d1$Reef.Rate.Fuel.RangeLow)
d1$BackHaul <- factor(d1$BackHaul, levels = c("YES" ,"NO"), labels = c("Yes", "No"))
load <- read.csv("load.csv", header = TRUE)
load$X <- NULL
load$Opportunity.Amount.Van.millions. <- str_remove(load$Opportunity.Amount.Van.millions., "[m]")
load$Opportunity.Amount.Reefer..millions. <- str_remove(load$Opportunity.Amount.Reefer..millions., "[m]")
load$Difference.Avalible.Loads..V.R <- NULL
load$Difference.posted.vs.actual.paid.RPM...Van. <- NULL
load$Difference.posted.vs.actual.paid.RatePerMile...Reefer. <- NULL
load$Time..Central.US..1 <- NULL
load$AM.PM.1 <- NULL
load$Date.1 <- NULL
load$Day.1 <- NULL
load$Total.Avalible.Loads.Per.Hour.per.Day.for.48.States <- NULL
load$Avalible.loads.per.State <- NULL
load$State <- NULL
load$Country <- NULL
load$Opportunity.Amount.Reefer..millions.  <- as.numeric(load$Opportunity.Amount.Reefer..millions. )
load$Opportunity.Amount.Van.millions. <- as.numeric(load$Opportunity.Amount.Van.millions.)


```

### Variable Clustering - Van

```{r}
vc <- Hmisc::varclus(~Month + Actual.Fuel+Est.Fuel.Van+Miles+Acutal.Rate.Van.NoFuel+Acutal.Rate.Van.Fuel+Fuel.Van+BackHaul+Van.Rate.Fuel.RangeLow+Van.Rate.Fuel.RangeHigh + Van.PerTrip, data = d1, similarity = "hoeffding")
plot(vc)
```

### Van (Elastic Net Model) - No Fuel

```{r}
# d1 <- d1[sample(nrow(d1), size = 12, replace = TRUE), ]
x <- model.matrix( ~ Actual.Fuel+Est.Fuel.Van+Miles+Fuel.Van+BackHaul+Van.Rate.Fuel.RangeLow+Van.Rate.Fuel.RangeHigh+Van.PerTrip, d1)
y1 <- as.matrix(d1[, 13])
y2 <- as.matrix(d1[, 14])
dd1 <- glmnet(x, y1, alpha = 0.5)
plot(dd1)
aa <- cv.glmnet(x, y1, type.measure = "mse")
dd1 <- glmnet(x, y1, alpha = 1, lambda = aa$lambda.min)
coef(dd1)
est <- predict(dd1, newx = x)
write.csv(est, file = "est.csv")




this.sample <- list()
x.sample <- list()
y.sample <- list()
aa <- list()
mm <- list()
pred <- list()
pp <- list()
for (i in 1:30) {
  this.sample[[i]] <- d1[sample(nrow(d1), size = 12, replace = TRUE), ]
  this.sample[[i]]$Intercept <- NULL
 x.sample[[i]]<- model.matrix(~ Actual.Fuel+ Est.Fuel.Van +Miles+Fuel.Van+BackHaul+Van.Rate.Fuel.RangeLow+Van.Rate.Fuel.RangeHigh+Van.PerTrip, this.sample[[i]])
  y.sample[[i]] <- as.matrix(this.sample[[i]][,13])
 aa[[i]] <- cv.glmnet(x.sample[[i]], y.sample[[i]], type.measure = "mse")
 mm[[i]] <- glmnet(x.sample[[i]], y.sample[[i]], alpha = 0.5, lambda = aa[[i]]$lambda.min)
 pred[[i]] <- predict(mm[[i]], newx = x.sample[[i]])
 pred[[i]] <- as.data.frame(pred[[i]])
 pred[[i]]$ID <- round(as.numeric(rownames(pred[[i]])))
 rownames(pred[[i]]) <- NULL
 pp[[i]] <- unique(pred[[i]])
}

ab <- as.data.frame(c(1:15))
names(ab)[1] <- "ID"

dd1 <- left_join(ab, pp[[1]], by = "ID")
dd2 <- left_join(dd1, pp[[2]], by = "ID")
dd3 <- left_join(dd2, pp[[3]], by = "ID")
dd4 <- left_join(dd3, pp[[4]], by = "ID")
dd5 <- left_join(dd4, pp[[5]], by = "ID")
dd6 <- left_join(dd5, pp[[6]], by = "ID")
dd7 <- left_join(dd6, pp[[7]], by = "ID")
dd8 <- left_join(dd7, pp[[8]], by = "ID")
dd9 <- left_join(dd8, pp[[9]], by = "ID")
dd10 <- left_join(dd9, pp[[10]], by = "ID")
dd11 <- left_join(dd10, pp[[11]], by = "ID")
dd12 <- left_join(dd11, pp[[12]], by = "ID")
dd13 <- left_join(dd12, pp[[13]], by = "ID")
dd14 <- left_join(dd13, pp[[14]], by = "ID")
dd15 <- left_join(dd14, pp[[15]], by = "ID")
dd16 <- left_join(dd15, pp[[16]], by = "ID")
dd17 <- left_join(dd16, pp[[17]], by = "ID")
dd18 <- left_join(dd17, pp[[18]], by = "ID")
dd19 <- left_join(dd18, pp[[19]], by = "ID")
dd20 <- left_join(dd19, pp[[20]], by = "ID")
dd21 <- left_join(dd20, pp[[21]], by = "ID")
dd22 <- left_join(dd21, pp[[22]], by = "ID")
dd23 <- left_join(dd22, pp[[23]], by = "ID")
dd24 <- left_join(dd23, pp[[24]], by = "ID")
dd25 <- left_join(dd24, pp[[25]], by = "ID")
dd26 <- left_join(dd25, pp[[26]], by = "ID")
dd27 <- left_join(dd26, pp[[27]], by = "ID")
dd28 <- left_join(dd27, pp[[28]], by = "ID")
dd29 <- left_join(dd28, pp[[29]], by = "ID")
dd30 <- left_join(dd29, pp[[30]], by = "ID")
dd <- dd30

RowMean <- rowMeans(dd, na.rm = TRUE)
ab$Van <- RowMean
ab$sd <- transform(dd[,2:31], SD=apply(dd[,2:31],1, sd, na.rm = TRUE))$SD
ab$N <- rowSums(is.na(dd[, 2:31]))
ab$se <- ab$sd / sqrt(ab$N)
ab$lower <- ab$Van - 1.96*ab$se
ab$upper <- ab$Van + 1.96*ab$se

write.csv(ab, file = "ab.csv")


```

- Van rate for No Fuel: $y=0.287 - 0.1568*Acuaal.Fuel - 1.5581*Est.Fuel.Van + 0.0000087*Miles + 0.4163*Va.Rate.Fule.RangeLow + 0.5243*Van.Rate.Fuel.RangeHigh-0.0000031Van.PerTrip$

### Van (Elastic Net Model) - Fuel

```{r}
# x <- as.matrix(d1[,c(3,4,6,15,17, 20,21)])
x <- model.matrix( ~ Actual.Fuel+Est.Fuel.Van+Miles+Fuel.Van+BackHaul+Van.Rate.Fuel.RangeLow+Van.Rate.Fuel.RangeHigh+Van.PerTrip, d1)
y1 <- as.matrix(d1[, 13])
y2 <- as.matrix(d1[, 14])
dd1 <- glmnet(x, y2, alpha = 0.5)
plot(dd1)
cv.glmnet(x, y2, type.measure = "mse")
dd1 <- glmnet(x, y2, alpha = 0.5, lambda = 0.0076)
coef(dd1)
pred <- predict(dd1, newx = x)
write.csv(pred, file = "pred.csv")



this.sample <- list()
x.sample <- list()
y.sample <- list()
aa <- list()
mm <- list()
pred <- list()
pp <- list()
for (i in 1:30) {
  this.sample[[i]] <- d1[sample(nrow(d1), size = 12, replace = TRUE), ]
  this.sample[[i]]$Intercept <- NULL
 x.sample[[i]]<- model.matrix( ~ Actual.Fuel+Est.Fuel.Van+Miles+Fuel.Van+BackHaul+Van.Rate.Fuel.RangeLow+Van.Rate.Fuel.RangeHigh+Van.PerTrip, this.sample[[i]])
  y.sample[[i]] <- as.matrix(this.sample[[i]][,14])
 aa[[i]] <- cv.glmnet(x.sample[[i]], y.sample[[i]], type.measure = "mse")
 mm[[i]] <- glmnet(x.sample[[i]], y.sample[[i]], alpha = 0.5, lambda = aa[[i]]$lambda.min)
 pred[[i]] <- predict(mm[[i]], newx = x.sample[[i]])
 pred[[i]] <- as.data.frame(pred[[i]])
 pred[[i]]$ID <- round(as.numeric(rownames(pred[[i]])))
 rownames(pred[[i]]) <- NULL
 pp[[i]] <- unique(pred[[i]])
}

ab <- as.data.frame(c(1:15))
names(ab)[1] <- "ID"

dd1 <- left_join(ab, pp[[1]], by = "ID")
dd2 <- left_join(dd1, pp[[2]], by = "ID")
dd3 <- left_join(dd2, pp[[3]], by = "ID")
dd4 <- left_join(dd3, pp[[4]], by = "ID")
dd5 <- left_join(dd4, pp[[5]], by = "ID")
dd6 <- left_join(dd5, pp[[6]], by = "ID")
dd7 <- left_join(dd6, pp[[7]], by = "ID")
dd8 <- left_join(dd7, pp[[8]], by = "ID")
dd9 <- left_join(dd8, pp[[9]], by = "ID")
dd10 <- left_join(dd9, pp[[10]], by = "ID")
dd11 <- left_join(dd10, pp[[11]], by = "ID")
dd12 <- left_join(dd11, pp[[12]], by = "ID")
dd13 <- left_join(dd12, pp[[13]], by = "ID")
dd14 <- left_join(dd13, pp[[14]], by = "ID")
dd15 <- left_join(dd14, pp[[15]], by = "ID")
dd16 <- left_join(dd15, pp[[16]], by = "ID")
dd17 <- left_join(dd16, pp[[17]], by = "ID")
dd18 <- left_join(dd17, pp[[18]], by = "ID")
dd19 <- left_join(dd18, pp[[19]], by = "ID")
dd20 <- left_join(dd19, pp[[20]], by = "ID")
dd21 <- left_join(dd20, pp[[21]], by = "ID")
dd22 <- left_join(dd21, pp[[22]], by = "ID")
dd23 <- left_join(dd22, pp[[23]], by = "ID")
dd24 <- left_join(dd23, pp[[24]], by = "ID")
dd25 <- left_join(dd24, pp[[25]], by = "ID")
dd26 <- left_join(dd25, pp[[26]], by = "ID")
dd27 <- left_join(dd26, pp[[27]], by = "ID")
dd28 <- left_join(dd27, pp[[28]], by = "ID")
dd29 <- left_join(dd28, pp[[29]], by = "ID")
dd30 <- left_join(dd29, pp[[30]], by = "ID")
dd <- dd30

RowMean <- rowMeans(dd, na.rm = TRUE)
ab$Van <- RowMean
ab$sd <- transform(dd[,2:31], SD=apply(dd[,2:31],1, sd, na.rm = TRUE))$SD
ab$N <- rowSums(is.na(dd[, 2:31]))
ab$se <- ab$sd / sqrt(ab$N)
ab$lower <- ab$Van - 1.96*ab$se
ab$upper <- ab$Van + 1.96*ab$se

write.csv(ab, file = "ab.csv")


```

- Van rate for Fuel: $y=0.3131 - 0.3915*Acuaal.Fuel - 1.6*Est.Fuel.Van + 0.0000388*Miles + 0.36*Va.Rate.Fule.RangeLow + 0.5793*Van.Rate.Fuel.RangeHigh$


### Variable Clustering - Reef

```{r}
vc <- varclus(~Month + Actual.Fuel+Miles+Acutal.Rate.Reef.NoFuel+Acutal.Rate.Reef.Fuel+Acutal.Rate.Reef.NoFuel.LOW+Fuel.Reef+Reef.PerTrip+Reef.PerTrip+BackHaul+Reef.Rate.Fuel.RangeLow+Reef.Rate.Fuel.RangeHigh, data = d1, similarity = "hoeffding")
plot(vc)

```

### Reef (Elastic Net Model) - Fuel

```{r}
x <- model.matrix( ~ Actual.Fuel+Miles+Acutal.Rate.Reef.NoFuel.LOW+Fuel.Reef+Reef.PerTrip+Reef.PerTrip+BackHaul+Reef.Rate.Fuel.RangeLow+Reef.Rate.Fuel.RangeHigh, d1)
y1 <- as.matrix(d1[, 8])
y2 <- as.matrix(d1[, 9])
dd1 <- glmnet(x, y1, alpha = 0.5)
plot(dd1)
cv.glmnet(x, y1, type.measure = "mse")
dd1 <- glmnet(x, y1, alpha = 0.5, lambda = 0.0372)
coef(dd1)

pred <- predict(dd1, newx = x)




this.sample <- list()
x.sample <- list()
y.sample <- list()
aa <- list()
mm <- list()
pred <- list()
pp <- list()
for (i in 1:30) {
  this.sample[[i]] <- d1[sample(nrow(d1), size = 12, replace = TRUE), ]
  this.sample[[i]]$Intercept <- NULL
 x.sample[[i]]<- model.matrix( ~ Actual.Fuel+Miles+Acutal.Rate.Reef.NoFuel.LOW+Fuel.Reef+Reef.PerTrip+Reef.PerTrip+BackHaul+Reef.Rate.Fuel.RangeLow+Reef.Rate.Fuel.RangeHigh, this.sample[[i]])
  y.sample[[i]] <- as.matrix(this.sample[[i]][,8])
 aa[[i]] <- cv.glmnet(x.sample[[i]], y.sample[[i]], type.measure = "mse")
 mm[[i]] <- glmnet(x.sample[[i]], y.sample[[i]], alpha = 0.5, lambda = aa[[i]]$lambda.min)
 pred[[i]] <- predict(mm[[i]], newx = x.sample[[i]])
 pred[[i]] <- as.data.frame(pred[[i]])
 pred[[i]]$ID <- round(as.numeric(rownames(pred[[i]])))
 rownames(pred[[i]]) <- NULL
 pp[[i]] <- unique(pred[[i]])
}

ab <- as.data.frame(c(1:15))
names(ab)[1] <- "ID"

dd1 <- left_join(ab, pp[[1]], by = "ID")
dd2 <- left_join(dd1, pp[[2]], by = "ID")
dd3 <- left_join(dd2, pp[[3]], by = "ID")
dd4 <- left_join(dd3, pp[[4]], by = "ID")
dd5 <- left_join(dd4, pp[[5]], by = "ID")
dd6 <- left_join(dd5, pp[[6]], by = "ID")
dd7 <- left_join(dd6, pp[[7]], by = "ID")
dd8 <- left_join(dd7, pp[[8]], by = "ID")
dd9 <- left_join(dd8, pp[[9]], by = "ID")
dd10 <- left_join(dd9, pp[[10]], by = "ID")
dd11 <- left_join(dd10, pp[[11]], by = "ID")
dd12 <- left_join(dd11, pp[[12]], by = "ID")
dd13 <- left_join(dd12, pp[[13]], by = "ID")
dd14 <- left_join(dd13, pp[[14]], by = "ID")
dd15 <- left_join(dd14, pp[[15]], by = "ID")
dd16 <- left_join(dd15, pp[[16]], by = "ID")
dd17 <- left_join(dd16, pp[[17]], by = "ID")
dd18 <- left_join(dd17, pp[[18]], by = "ID")
dd19 <- left_join(dd18, pp[[19]], by = "ID")
dd20 <- left_join(dd19, pp[[20]], by = "ID")
dd21 <- left_join(dd20, pp[[21]], by = "ID")
dd22 <- left_join(dd21, pp[[22]], by = "ID")
dd23 <- left_join(dd22, pp[[23]], by = "ID")
dd24 <- left_join(dd23, pp[[24]], by = "ID")
dd25 <- left_join(dd24, pp[[25]], by = "ID")
dd26 <- left_join(dd25, pp[[26]], by = "ID")
dd27 <- left_join(dd26, pp[[27]], by = "ID")
dd28 <- left_join(dd27, pp[[28]], by = "ID")
dd29 <- left_join(dd28, pp[[29]], by = "ID")
dd30 <- left_join(dd29, pp[[30]], by = "ID")
dd <- dd30

RowMean <- rowMeans(dd, na.rm = TRUE)
ab$Van <- RowMean
ab$sd <- transform(dd[,2:31], SD=apply(dd[,2:31],1, sd, na.rm = TRUE))$SD
ab$N <- rowSums(is.na(dd[, 2:31]))
ab$se <- ab$sd / sqrt(ab$N)
ab$lower <- ab$Van - 1.96*ab$se
ab$upper <- ab$Van + 1.96*ab$se

write.csv(ab, file = "ab.csv")

```



```{r}
dd1 <- glmnet(x, y2, alpha = 0.5)
aa <- cv.glmnet(x, y2, type.measure = "mse")
dd1 <- glmnet(x, y2, alpha = 0.5, lambda = aa$lambda.min)
coef(dd1)
pred <- predict(dd1, newx = x)
write.csv(pred, file = "pred.csv")

this.sample <- list()
x.sample <- list()
y.sample <- list()
aa <- list()
mm <- list()
pred <- list()
pp <- list()
for (i in 1:30) {
  this.sample[[i]] <- d1[sample(nrow(d1), size = 12, replace = TRUE), ]
  this.sample[[i]]$Intercept <- NULL
 x.sample[[i]]<- model.matrix( ~ Actual.Fuel+Miles+Acutal.Rate.Reef.NoFuel.LOW+Fuel.Reef+Reef.PerTrip+Reef.PerTrip+BackHaul+Reef.Rate.Fuel.RangeLow+Reef.Rate.Fuel.RangeHigh, this.sample[[i]])
  y.sample[[i]] <- as.matrix(this.sample[[i]][,9])
 aa[[i]] <- cv.glmnet(x.sample[[i]], y.sample[[i]], type.measure = "mse")
 mm[[i]] <- glmnet(x.sample[[i]], y.sample[[i]], alpha = 0.5, lambda = aa[[i]]$lambda.min)
 pred[[i]] <- predict(mm[[i]], newx = x.sample[[i]])
 pred[[i]] <- as.data.frame(pred[[i]])
 pred[[i]]$ID <- round(as.numeric(rownames(pred[[i]])))
 rownames(pred[[i]]) <- NULL
 pp[[i]] <- unique(pred[[i]])
}

ab <- as.data.frame(c(1:15))
names(ab)[1] <- "ID"

dd1 <- left_join(ab, pp[[1]], by = "ID")
dd2 <- left_join(dd1, pp[[2]], by = "ID")
dd3 <- left_join(dd2, pp[[3]], by = "ID")
dd4 <- left_join(dd3, pp[[4]], by = "ID")
dd5 <- left_join(dd4, pp[[5]], by = "ID")
dd6 <- left_join(dd5, pp[[6]], by = "ID")
dd7 <- left_join(dd6, pp[[7]], by = "ID")
dd8 <- left_join(dd7, pp[[8]], by = "ID")
dd9 <- left_join(dd8, pp[[9]], by = "ID")
dd10 <- left_join(dd9, pp[[10]], by = "ID")
dd11 <- left_join(dd10, pp[[11]], by = "ID")
dd12 <- left_join(dd11, pp[[12]], by = "ID")
dd13 <- left_join(dd12, pp[[13]], by = "ID")
dd14 <- left_join(dd13, pp[[14]], by = "ID")
dd15 <- left_join(dd14, pp[[15]], by = "ID")
dd16 <- left_join(dd15, pp[[16]], by = "ID")
dd17 <- left_join(dd16, pp[[17]], by = "ID")
dd18 <- left_join(dd17, pp[[18]], by = "ID")
dd19 <- left_join(dd18, pp[[19]], by = "ID")
dd20 <- left_join(dd19, pp[[20]], by = "ID")
dd21 <- left_join(dd20, pp[[21]], by = "ID")
dd22 <- left_join(dd21, pp[[22]], by = "ID")
dd23 <- left_join(dd22, pp[[23]], by = "ID")
dd24 <- left_join(dd23, pp[[24]], by = "ID")
dd25 <- left_join(dd24, pp[[25]], by = "ID")
dd26 <- left_join(dd25, pp[[26]], by = "ID")
dd27 <- left_join(dd26, pp[[27]], by = "ID")
dd28 <- left_join(dd27, pp[[28]], by = "ID")
dd29 <- left_join(dd28, pp[[29]], by = "ID")
dd30 <- left_join(dd29, pp[[30]], by = "ID")
dd <- dd30

RowMean <- rowMeans(dd, na.rm = TRUE)
ab$Van <- RowMean
ab$sd <- transform(dd[,2:31], SD=apply(dd[,2:31],1, sd, na.rm = TRUE))$SD
ab$N <- rowSums(is.na(dd[, 2:31]))
ab$se <- ab$sd / sqrt(ab$N)
ab$lower <- ab$Van - 1.96*ab$se
ab$upper <- ab$Van + 1.96*ab$se

write.csv(ab, file = "ab.csv")
```

- Reef with No Fuel: $y=0.313 - 0.3915*Acutal.Fuel - 1.6*Est.Fuel.Van + 0.0000388*Miles + 0.36*Van.Rate.Fuel.RangeLow+0.579*Van.Rate.Fuel.RangeHigh$


## d2 dataset - For Van Only

### Low.Rate.Per.Mile.van.

```{r}
d2 <- d2[complete.cases(d2), ]
x <- as.matrix(d2[, c(6, 11:13)])
y1 <- as.matrix(d2[, 7])
y2 <- as.matrix(d2[, 8])
y3 <- as.matrix(d2[, 9])
y4 <- as.matrix(d2[, 10])

dd <- glmnet(x, y1, alpha = 1)
plot(dd)
cv.glmnet(x, y1, type.measure = "mse")
dd1 <- glmnet(x, y1, alpha = 1, lambda = 0.00069)
coef(dd1)

d2$pred <- predict(dd1, newx = x)
d2$Lane.Pairs <- as.factor(d2$Lane.Pairs)
d2 %>%
  group_by(Lane.Pairs) %>%
  summarise( mean(pred, na.rm = T))

```

- $ Low.Rate.Per.Mile.van. = 1.596 - 0.00145*Miles.Estimate + 0.000816*Median.Total.Without.Fuel.surcharge.LineHaul.Van$


### Median.Rate.Per.Mile.Van

```{r}
x <- as.matrix(d2[, c(6, 11:13)])
y2 <- as.matrix(d2[, 8])

dd <- glmnet(x, y2, alpha = 1)
plot(dd)
cv.glmnet(x, y2, type.measure = "mse")
dd1 <- glmnet(x, y2, alpha = 1, lambda = 0.00072)
coef(dd1)
```

- $ Median.Rate.Per.Mile.Van = 1.788 - 0.00153*Miles.Estimate + 0.000854*Median.Total.Without.Fuel.surcharge.LineHaul.Van$

### Estimate.Average.Rate.Per.Mile.Van

```{r}
x <- as.matrix(d2[, c(6, 11:13)])
y3 <- as.matrix(d2[, 9])

dd <- glmnet(x, y3, alpha = 1)
plot(dd)
cv.glmnet(x, y3, type.measure = "mse")
dd1 <- glmnet(x, y3, alpha = 1, lambda = 0.00071)
coef(dd1)

d2$pred <- predict(dd1, newx = x)
d2$Lane.Pairs <- as.factor(d2$Lane.Pairs)
d2 %>%
  group_by(Lane.Pairs) %>%
  summarise( mean(pred, na.rm = T))
```

- $ Estimate.Average.Rate.Per.Mile.Van = 1.788 - 0.00151*Miles.Estimate + 0.000846*Median.Total.Without.Fuel.surcharge.LineHaul.Van$

### High.Rate.Per.Mile.Van

```{r}
x <- as.matrix(d2[, c(6, 11:13)])
y4 <- as.matrix(d2[, 10])

dd <- glmnet(x, y4, alpha = 1)
plot(dd)
cv.glmnet(x, y4, type.measure = "mse")
dd1 <- glmnet(x, y4, alpha = 1, lambda = 0.00081)
coef(dd1)
```

- $ High.Rate.Per.Mile.Van = 1.98 - 0.0016*Miles.Estimate + 0.00089*Median.Total.Without.Fuel.surcharge.LineHaul.Van$


## Load Data

### Variable Cluster - Van

```{r}
vc <- varclus(~Day + AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Avg.Paid.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load, similarity = "hoeffding")
plot(vc)
```

## LASSO Model - Van

```{r}
# x <- as.matrix(load[, c(2,4,5,7,13)])
x <- model.matrix( ~ AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Posted.Avg.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, load)
y <- as.matrix(load[, 10])

dd <- glmnet(x,y,alpha = 1)
plot(dd)
cv.glmnet(x, y, type.measure = "mse")
dd <- glmnet(x,y,alpha = 1, lambda = 0.00169)
coef(dd)
```

- $Avergage..Posted..RPM..Reefer. = -1.891+ 0.00345*Opportunity.Amount.Van.millions. - 0.0057*Avg.Paid.RPM.Van + 2.248*Posted.Avg.RPM.Van$

### Variable Cluster - Reef

```{r}
vc <- varclus(~Day + AM.PM + Opportunity.Amount.Reefer..millions. + Loads.Avalible.Reefer + Avergage..Posted..RPM..Reefer. + Average..Actual.Paid..RatePerMile..Reefer..per.Hour.and.Date + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load, similarity = "hoeffding")
plot(vc)
```

## LASSO Model - Reef

```{r}
# x <- as.matrix(load[, c(2,4,5,7,13)])
x <- model.matrix( ~ AM.PM + Opportunity.Amount.Reefer..millions. + Loads.Avalible.Reefer + Avergage..Posted..RPM..Reefer. + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, load)
y <- as.matrix(load[, 12])

dd <- glmnet(x,y,alpha = 1)
plot(dd)
cv.glmnet(x, y, type.measure = "mse")
dd <- glmnet(x,y,alpha = 1, lambda = 0.00205)
coef(dd)
```

- $Average..Actual.Paid..RatePerMile..Reefer..per.Hour.and.Date = 0.6416 + 0.0067*AM.PM(PM) - 0.00000637*Loads.Avalible.Reefer + 1.433 * Avergage..Posted..RPM..Reefer. - 0.464*Percentage.of.Loads.Avalible.by.state.per.day.per.Hour$


## Random Forest - Van

```{r}
require(randomForest)
require(tree)
require(party)
#library(reprtree)

f1 <- randomForest(Avg.Paid.RPM.Van ~ AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Posted.Avg.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load, importance = TRUE, ntree=500, mtry = 2, do.trace=100)
importance(f1)
plot(f1)


```

## Decision Tree - Van

```{r}
tr <- ctree(Avg.Paid.RPM.Van ~ AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Posted.Avg.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load)
plot(tr)
```

## Random Forest - Reef

```{r}

f1 <- randomForest(Average..Actual.Paid..RatePerMile..Reefer..per.Hour.and.Date ~ AM.PM + Opportunity.Amount.Reefer..millions. + Loads.Avalible.Reefer + Avergage..Posted..RPM..Reefer. + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load, importance = TRUE, ntree=500, mtry = 2, do.trace=100)
importance(f1)
plot(f1)


```

## Decision Tree - Reef

```{r}
tr <- ctree(Average..Actual.Paid..RatePerMile..Reefer..per.Hour.and.Date ~ AM.PM + Opportunity.Amount.Reefer..millions. + Loads.Avalible.Reefer + Avergage..Posted..RPM..Reefer. + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, data = load)
plot(tr)
```

## xgboost Model

```{r}
require(xgboost)
set.seed(1234)
index <- sample(1:66, 50)

train <- load[index, ]
test <- load[-index, ]


x.train <- model.matrix( ~ AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Posted.Avg.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, train)
y.train <- as.matrix(train[, 10])

x.test <- model.matrix( ~ AM.PM + Opportunity.Amount.Van.millions. + Loads.Avalible.Van + Posted.Avg.RPM.Van + Percentage.of.Loads.Avalible.by.state.per.day.per.Hour, test)
y.test <- as.matrix(test[,10])

dtrain <- xgb.DMatrix(data = x.train,label = y.train)
dtest <- xgb.DMatrix(data = x.test,label=y.test)

xgb1 <- xgboost(data = x.train, label = y.train, max.depth = 200, eta = 1, nthread = 2, nrounds = 2)

xgbpred <- predict (xgb1,newdata = x.test)
cbind(Original = y.test, Pred = xgbpred)
```
