from turtle import Turtle

ALIGNMENT = "center"
FONT = ("Courier", 16, 'normal')


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.high_score = 0
        self.score = 0
        self.color("white")
        self.hideturtle()
        self.penup()
        self.goto(0, 270)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        with open("high_score_file.txt", mode="r") as score_data:
            self.high_score = int(score_data.read())
        self.write(f"Score: {self.score}    Highest Score: {self.high_score}", align="center",
                   font=("Arial", 16, 'normal'))

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def reset(self):
        if self.score > self.high_score:
            with open("high_score_file.txt", "w") as new_file:
                new_file.write(str(self.score))
        self.score = 0
        self.update_scoreboard()
