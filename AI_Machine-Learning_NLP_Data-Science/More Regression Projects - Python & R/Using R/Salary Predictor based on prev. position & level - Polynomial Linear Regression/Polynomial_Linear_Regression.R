# 1. DATA PREPROCESSING

# Loading the dataset
df = read.csv('Position_Salaries.csv')
df = df[2:3]

# Handling missing data/values
# df$Age = ifelse(is.na(df$Age), 
#                 ave(df$Age, FUN = function(x) mean(x, na.rm = TRUE)),
#                 df$Age)

# df$Salary = ifelse(is.na(df$Salary), 
#                    ave(df$Salary, FUN = function(x) mean(x, na.rm = TRUE)),
#                    df$Salary)

# Encoding the categorical data
# df_startups$Country = factor(df_startups$State, 
#                              levels = c('New York', 'California', 'Florida'),
#                              labels = c(1, 2, 3))

# Splitting the dataset into training and test sets
# library(caTools)
# 
# set.seed(42)
# split = sample.split(df_startups$Profit, SplitRatio = 0.8)
# training_set = subset(df_startups, split == TRUE)
# test_set = subset(df_startups, split == FALSE)

# Feature Scaling
# training_set = scale(training_set)
# test_set = scale(test_set)


# Fitting Linear Regression to the dataset
lin_reg = lm(formula = Salary ~ .,
             data = df)

# Fitting Polynomial Regression to the dataset
df$Level2 = df$Level^2 # The number of degree is 2
df$Level3 = df$Level^3 # The number of degree is 3
df$Level4 = df$Level^4 # The number of degree is 3
poly_reg = lm(formula = Salary ~ .,
                  data = df)

install.packages('ggplot2')
library(ggplot2)

# Visualising the Linear Regression Results
ggplot() +
  geom_point(aes(x = df$Level, y = df$Salary),
             colour = 'red') +
  geom_line(aes(x = df$Level, y = predict(lin_reg, newdata = df)),
             colour = 'blue') +
  ggtitle('Truth or Bluff (Linear Regression)') +
  xlab('Level') +
  ylab('Salary')

# Visualising the Polynomial Regression Results (for higher resolution and smoother curve)
x_grid = seq(min(df$Level), max(df$Level), 0.1)
ggplot() +
  geom_point(aes(x = df$Level, y = df$Salary),
             colour = 'red') +
  geom_line(aes(x = x_grid, y = predict(poly_reg, newdata = data.frame(Level = x_grid))),
            colour = 'blue') +
  ggtitle('Truth or Bluff (Polynomial Regression)') +
  xlab('Level') +
  ylab('Salary')

# Predicting a new result (salary) with Linear Regression
y_pred = predict(lin_reg, data.frame(Level = 6.5))

# Predicting a new result (salary) with Polynomial Regression
y_poly_pred = predict(poly_reg, data.frame(Level = 6.5,
                                           Level2 = 6.5^2,
                                           Level3 = 6.5^3,
                                           Level4 = 6.5^4))
