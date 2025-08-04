class QuizBrain:

    def __init__(self, q_list):
        self.question_number = 0
        self.question_list = q_list
        self.score = 0
        self.pass_mark_in_percentage = 80
        self.total_percentage_score = 0

    def next_question(self):
        current_question = self.question_list[self.question_number]
        self.question_number += 1
        user_answer = input(f"\nQ.{self.question_number}: {current_question.text} (True or False)?: ").lower()
        self.check_answer(user_answer, current_question.answer)

    def still_has_question(self):
        return self.question_number < len(self.question_list)

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer.lower():
            self.score += 1
            print("     You got it right!")
        else:
            print("     Too bad, you got it wrong.")

        print(f"     The correct answer was '{correct_answer}'.")
        if self.score <= 1:
            print(f"     You got {self.score} point out of {self.question_number}.")
        elif self.score > 1:
            print(f"     You got {self.score} points out of {self.question_number}.")

    def calculate_percentage_score(self):
        questions_equivalent_percent_100 = round((len(self.question_list) / len(self.question_list)) * 100)
        self.total_percentage_score += (self.score / len(self.question_list)) * questions_equivalent_percent_100
        print("\n")
        if self.total_percentage_score >= self.pass_mark_in_percentage:
            print("Congratulations! You passed the quiz.")
        else:
            print("Sorry, you failed the quiz. Give it another try next time.")
        print(f"Your Total Points: {self.score}/{self.question_number}")
        print(f"Your Total Percentage Score: {round(self.total_percentage_score)}%")
        print(f"Out of: {questions_equivalent_percent_100}%.")
