from turtle import Turtle, Screen

screen = Screen()


class Paddles(Turtle):

    def __init__(self, position):
        super().__init__()
        self.speed("fastest")
        self.color("white")
        self.shape("square")
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.penup()
        self.goto(position)
        self.showturtle()

    def up(self):
        new_y = self.ycor() + 30
        if new_y < (screen.window_height() / 2) - 35:
            self.goto(self.xcor(), new_y)

    def down(self):
        new_y = self.ycor() - 30
        if new_y > -(screen.window_height() / 2) + 35:
            self.goto(self.xcor(), new_y)
    
    
