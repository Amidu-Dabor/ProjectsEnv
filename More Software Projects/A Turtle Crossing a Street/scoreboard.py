from turtle import Turtle


FONT = ("Courier", 24, "normal")


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.level = 0
        self.penup()
        self.hideturtle()
        self.goto(x=-280, y=260)
        self.display_level()

    def display_level(self):
        self.clear()
        self.write(f"Level: {self.level}", font=FONT)

    def increase_difficulty__level(self):
        self.level += 1
        self.display_level()

    def game_over(self):
        self.home()
        self.write("GAME OVER!", align="center", font=FONT)

