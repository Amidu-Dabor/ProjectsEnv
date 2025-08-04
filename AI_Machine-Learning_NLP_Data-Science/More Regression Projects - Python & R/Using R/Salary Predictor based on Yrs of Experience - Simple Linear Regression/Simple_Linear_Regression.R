# Simple Linear Regression

# Set the working directory
setwd('/Users/apple/PycharmProjects/AI_ML_Robotics_Data Science_Bootcamps/Machine Learning-A-Z - Python & R/2. Part 2 - Regression/Using R/1. Simple Linear Regression/')

# Loading the dataset
df = read.csv('Salary_Data.csv')

# Splitting the dataset into the training and test set
library(caTools)

set.seed(123)
split = sample.split(df$Salary, SplitRatio = 2/3) # 20 observations training set, 10 for test set
training_set = subset(df, split == TRUE)
test_set = subset(df, split == FALSE)

# Feature Scaling - The LinearRegression() model automatically takes care of the scaling.

# Fitting the Simple Linear Regressor to the Training Set
regressor = lm(formula = Salary ~ YearsExperience,
               data = training_set)

# Predicting the test set results
y_pred = predict(regressor, newdata = test_set)
y_pred

# Visualizing the training set results
library(ggplot2)
# Loading the httpgd package for interactive graphics
library(httpgd)

hgd() # Start the HTTPGD device

ggplot() +
  # Plotting the observation points
  geom_point(aes(x = training_set$YearsExperience, y = training_set$Salary),
             colour = 'red') +
  # Plotting the regression line
  geom_line(aes(x = training_set$YearsExperience, y = predict(regressor, newdata = training_set)),
            colour = 'blue') +
  ggtitle('Salary vs Experience (Training Set)') +
  xlab('Years of Experience') +
  ylab('Salary')
