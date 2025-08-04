
import pandas as pd
import numpy as np
import random

# Set seed for reproducibility
np.random.seed(42)

# Parameters
n = 300
student_ids = range(1001, 1001 + n)
ages = np.random.randint(18, 36, size=n)
programs = ['Data Science', 'Cybersecurity', 'Applications', 'Networking', 'Artificial Intelligence']

# Gender with more missing values
gender_choices = ['M', 'F', None]
gender_probs = [0.45, 0.45, 0.10]
genders = np.random.choice(gender_choices, size=n, p=gender_probs)

# Names lists
male_names = ['Brian', 'Michael', 'David', 'James', 'Daniel', 'Robert', 'Joseph', 'John', 'Charles', 'William']
female_names = ['Alice', 'Mary', 'Linda', 'Susan', 'Karen', 'Patricia', 'Jennifer', 'Elizabeth', 'Sarah', 'Emily']
all_names = male_names + female_names

# Assign gender-appropriate names
names = [
    random.choice(male_names) if gender == 'M' else
    random.choice(female_names) if gender == 'F' else
    random.choice(all_names)
    for gender in genders
]

# Generate data
data_final = {
    "StudentID": student_ids,
    "Name": names,
    "Age": ages,
    "Gender": genders,
    "Program": np.random.choice(programs, size=n),
    "GPA": np.round(np.clip(np.random.normal(3.0, 0.6, size=n), 0, 4.0), 2),
    "StudyHours": np.random.randint(0, 25, size=n),
    "SleepHours": np.random.randint(3, 10, size=n),
    "ExerciseHours": np.random.randint(0, 7, size=n),
    "SocialMediaHours": np.random.randint(0, 8, size=n),
    "MoodLevel": np.random.randint(1, 11, size=n),
    "StressLevel": np.random.randint(1, 11, size=n),
    "AttendanceRate (%)": np.round(np.random.uniform(60, 100, size=n), 2)
}

df_final = pd.DataFrame(data_final)

# Add missing values in multiple columns
for col in ['GPA', 'StudyHours', 'SleepHours', 'ExerciseHours', 'AttendanceRate (%)']:
    df_final.loc[df_final.sample(frac=0.08).index, col] = np.nan

# Save to CSV
df_final.to_csv("student_wellbeing_final.csv", index=False)
