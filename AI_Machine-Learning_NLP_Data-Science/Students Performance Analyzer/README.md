# Student Wellbeing and Performance Analyzer

Analyses how students' habits (study, sleep, exercise, social media) and wellbeing (mood, stress) relate to their grades, using a reusable `StudentWellbeingAnalyzer` class.

## What it does

- Summarises and cleans missing values.
- Converts GPA into letter grades.
- Builds a combined **wellbeing score**.
- Runs univariate and bivariate analysis and compares performance across programmes.
- Prints key insights, for example that higher social-media use slightly lowers wellbeing.
- Exports the cleaned data to `cleaned_student_data.csv`.

The dataset is synthetic: `data_generation_code.py` creates 300 realistic student records with deliberate gaps to clean.

## Files

| File | Purpose |
|---|---|
| `students_performance_analyzer.ipynb` | The full analysis with charts |
| `student_analysis_exam.py` | The same analyser as a script |
| `data_generation_code.py` | Generates the synthetic dataset |
| `Students Performance Analyzer Project Report.pdf` | The write-up |

## Tech

Python · pandas · Matplotlib · Seaborn

## Run

```bash
pip install pandas matplotlib seaborn
python student_analysis_exam.py
```

*Built for the Data & AI programme at Cyber Shujaa, Kenya.*
