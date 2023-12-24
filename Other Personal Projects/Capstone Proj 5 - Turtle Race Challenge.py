from turtle import Turtle, Screen
import random

screen = Screen()
screen.setup(width=1100, height=700)
screen.listen()

colours = ["red", "orange", "yellow", "green", "blue", "purple"]
turtles = []
counter = -200
is_race_on = False

user_bet = screen.textinput(title="Turtle Race", prompt="Which turtle will win the race? Enter the colour as your bet: ")

for turtle_index in range(6):
    tut_name = Turtle(shape='turtle')
    tut_name.color(colours[turtle_index])
    tut_name.penup()
    tut_name.goto(x=-520, y=counter)
    turtles.append(tut_name)
    counter -= -60

if user_bet:
    is_race_on = True

while is_race_on:
    for turtle in turtles:
        if turtle.xcor() > ((screen.window_width() / 2) - (40 / 2)):
            is_race_on = False
            winner_colour = turtle.pencolor()
            if winner_colour == user_bet:
                print(f"You won! turtle with '{winner_colour}' colour is the winner.")
            else:
                print(f"You lost! turtle with '{winner_colour}' colour is the winner.")

        turtle.forward(random.choice(range(5, 21)))


print(f"Screen Width: {screen.window_width()}")
print(f"Screen Height: {screen.window_height()}")
print((Turtle().shapesize()))
print(Turtle().xcor())

screen.exitonclick()
