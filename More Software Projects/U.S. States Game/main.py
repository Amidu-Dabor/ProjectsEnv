import turtle

import pandas
import pandas as pd

screen = turtle.Screen()
screen.title("U.S. States Game")
bg_image = "blank_states_img.gif"
screen.addshape(bg_image)
turtle.shape(bg_image)

data = pd.read_csv("50_states.csv")
states_list = data.state.to_list()
guessed_states = []

while len(guessed_states) < 50:
    guess = screen.textinput(title=f"States Guess | {len(guessed_states)}/50",
                             prompt="What's the name of the next state on the map?").title()

    if guess == "Exit":
        missing_states = [st for st in states_list if st not in guessed_states]
        new_data = pandas.DataFrame(missing_states)
        new_data.to_csv("missing-states-to-learn.csv")
        break
    # Check if the guess is among the 50 states.
    if guess in states_list:
        guessed_states.append(guess)
        t = turtle.Turtle()
        t.hideturtle()
        t.penup()
        t.speed(0.09)
        state_data = data[guess == data.state]
        t.goto(int(state_data.x), int(state_data.y))
        t.write(arg=guess, move=True)

screen.mainloop()
