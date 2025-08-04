from turtle import Turtle
import random


class Food(Turtle):

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=0.6, stretch_wid=0.6)
        self.color("orange")
        self.speed("fastest")
        self.place_another_food()

    def place_another_food(self):
        random_x = random.randint(-280, 280)
        random_y = random.randint(-280, 240)
        self.goto(random_x, random_y)
