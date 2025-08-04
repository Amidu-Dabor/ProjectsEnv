# 1. DATA PREPROCESSING

# Loading the dataset
df = read.csv('Data.csv')

# Handling missing data/values
df$Age = ifelse(is.na(df$Age), 
                ave(df$Age, FUN = function(x) mean(x, na.rm = TRUE)),
                df$Age)

df$Salary = ifelse(is.na(df$Salary), 
                ave(df$Salary, FUN = function(x) mean(x, na.rm = TRUE)),
                df$Salary)

# Encoding the categorical data
df$Country = factor(df$Country, 
                    levels = c('France', 'Spain', 'Germany'),
                    labels = c(1, 2, 3))

df$Purchased = factor(df$Purchased, 
                    levels = c('Yes', 'No'),
                    labels = c(1, 0))

# Splitting the dataset into training and test sets
library(caTools)

set.seed(123)
split = sample.split(df$Purchased, SplitRatio = 0.8)
training_set = subset(df, split == TRUE)
test_set = subset(df, split == FALSE)

# Feature Scaling
training_set = scale(training_set)
test_set = scale(test_set)
