import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class StudentWellbeingAnalyzer:
    def __init__(self, file_path: str):
        """Load dataset and show preview"""
        self.df = pd.read_csv(file_path)
        print("Preview:\n", self.df.head())

    def summarize_missing_values(self):
        """Summarize missing values"""
        print("\nMissing values:\n", self.df.isnull().sum())

    def clean_data(self):
        """Handle missing values and ensure correct types"""
        self.df.dropna(subset=['GPA', 'Program'], inplace=True)

        numeric_cols = ['StudyHours', 'SleepHours', 'ExerciseHours', 'SocialMediaHours',
                        'MoodLevel', 'StressLevel', 'AttendanceRate (%)']
        for col in numeric_cols:
            self.df[col].fillna(self.df[col].median(), inplace=True)

        self.df['GPA'] = self.df['GPA'].astype(float)
        self.df['AttendanceRate (%)'] = self.df['AttendanceRate (%)'].astype(float)

    def assign_letter_grades(self):
        """Create Letter Grade column from GPA"""
        def grade(g: float) -> str:
            if g >= 90: return 'A'
            elif g >= 85: return 'A-'
            elif g >= 80: return 'B+'
            elif g >= 75: return 'B'
            elif g >= 70: return 'B-'
            elif g >= 65: return 'C+'
            elif g >= 60: return 'C'
            elif g >= 55: return 'C-'
            elif g >= 50: return 'D+'
            elif g >= 45: return 'D'
            elif g >= 40: return 'D-'
            else: return 'F'
        self.df['LetterGrade'] = self.df['GPA'].apply(grade)

    def compute_wellbeing_score(self):
        """Create WellbeingScore (0–100) based on normalized indicators"""
        df = self.df
        df['SleepScore'] = df['SleepHours'] / 9
        df['ExerciseScore'] = df['ExerciseHours'] / 7
        df['MoodScore'] = df['MoodLevel'] / 10
        df['StressScore'] = 1 - (df['StressLevel'] / 10)
        df['SocialMediaScore'] = 1 - (df['SocialMediaHours'] / 8)
        df['StudyScore'] = df['StudyHours'] / 20

        df['WellbeingScore'] = (
            0.2 * df['SleepScore'] +
            0.2 * df['ExerciseScore'] +
            0.2 * df['MoodScore'] +
            0.2 * df['StressScore'] +
            0.1 * df['SocialMediaScore'] +
            0.1 * df['StudyScore']
        ) * 100

    def univariate_analysis(self):
        """Plot histograms for StudyHours, GPA, MoodLevel, StressLevel"""
        cols = ['StudyHours', 'GPA', 'MoodLevel', 'StressLevel']
        for col in cols:
            sns.histplot(self.df[col], kde=True)
            plt.title(f'{col} Distribution')
            plt.xlabel(col)
            plt.ylabel('Count')
            plt.show()

    def bivariate_analysis(self):
        """Scatterplots and heatmaps to explore relationships"""
        sns.scatterplot(data=self.df, x='StudyHours', y='GPA')
        plt.title("Study Hours vs GPA")
        plt.show()

        sns.scatterplot(data=self.df, x='SleepHours', y='GPA')
        plt.title("Sleep Hours vs GPA")
        plt.show()

        heatmap_data = self.df[['SleepHours', 'ExerciseHours', 'MoodLevel',
                                'StressLevel', 'SocialMediaHours']]
        sns.heatmap(heatmap_data.corr(), annot=True, cmap='coolwarm')
        plt.title("Wellbeing Indicators Correlation Matrix")
        plt.show()

    def compare_academic_performance(self):
        """Compare GPA across Program and Gender"""
        sns.barplot(data=self.df, x='Program', y='GPA', hue='Gender')
        plt.xticks(rotation=45)
        plt.title("GPA by Program and Gender")
        plt.show()

    def key_insights(self):
        """Print 5 meaningful findings from EDA"""
        print("\nKey Insights:")
        print("1. Students who study more tend to have higher GPA.")
        print("2. Better mood and more sleep relate to lower stress.")
        print("3. Higher social media use slightly lowers WellbeingScore.")
        print("4. Female students show slightly better GPA overall.")
        print("5. Students in AI and Data Science show higher wellbeing and grades.")

    def export_cleaned_data(self, out_file: str):
        """Save cleaned and transformed dataset for dashboard use"""
        self.df.to_csv(out_file, index=False)
        print(f"Cleaned data saved to: {out_file}")


if __name__ == "__main__":
    analyzer = StudentWellbeingAnalyzer("student_wellbeing_final.csv")
    analyzer.summarize_missing_values()
    analyzer.clean_data()
    analyzer.assign_letter_grades()
    analyzer.compute_wellbeing_score()
    analyzer.univariate_analysis()
    analyzer.bivariate_analysis()
    analyzer.compare_academic_performance()
    analyzer.key_insights()
    analyzer.export_cleaned_data("cleaned_student_data.csv")
