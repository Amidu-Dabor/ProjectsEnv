# 1. DATA PREPROCESSING

# Loading the dataset
df_startups = read.csv('50_Startups.csv')

# Handling missing data/values
# df$Age = ifelse(is.na(df$Age), 
#                 ave(df$Age, FUN = function(x) mean(x, na.rm = TRUE)),
#                 df$Age)

# df$Salary = ifelse(is.na(df$Salary), 
#                    ave(df$Salary, FUN = function(x) mean(x, na.rm = TRUE)),
#                    df$Salary)

# Encoding the categorical data
df_startups$Country = factor(df_startups$State, 
                    levels = c('New York', 'California', 'Florida'),
                    labels = c(1, 2, 3))

# Splitting the dataset into training and test sets
library(caTools)

set.seed(42)
split = sample.split(df_startups$Profit, SplitRatio = 0.8)
training_set = subset(df_startups, split == TRUE)
test_set = subset(df_startups, split == FALSE)

# Feature Scaling
# training_set = scale(training_set)
# test_set = scale(test_set)

# Fitting the 'Multiple Linear Regression 'to the training set
# Fit the dependent and all the independent variables
reg_startups = lm(formula = Profit ~ .,
                training_set)

# Predicting the test set results -> Evaluating the model's performance
y_pred = predict(reg_startups, newdata = test_set)

# Building the optimal model using 'Background elimination'
# Step 2:
reg_startups = lm(formula = Profit ~ R.D.Spend + Administration + Marketing.Spend + State,
                  df_startups)

# Step 3:
# Summary results to find regressor with the highest 'P-values' to be removed.
summary(reg_startups)

# Step 4:
# Removing the low significant predictor (State)
reg_startups = lm(formula = Profit ~ R.D.Spend + Administration + Marketing.Spend,
                  df_startups)
# Summary results to find more regressor(s) with the highest 'P-values' to remove.
summary(reg_startups)

# Step 5:
# Removing the low significant predictor (Administration)
reg_startups = lm(formula = Profit ~ R.D.Spend + Marketing.Spend,
                  df_startups)
# Summary results to find more regressor(s) with the highest 'P-values' to remove.
summary(reg_startups)
