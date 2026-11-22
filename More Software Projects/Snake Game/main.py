from turtle import Screen, Turtle
from snake import Snake
from scoreboard import Scoreboard
from food import Food
import time

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snake Game")
screen.tracer(0)

line = Turtle()
snake = Snake()
food = Food()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, 'Left')
screen.onkey(snake.right, "Right")

line.color("white")
line.speed('fastest')
line.hideturtle()
line.penup()
line.goto(-300, 255)
line.pendown()
line.forward(600)

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)

    # Call the snake to move
    snake.move()

    # Detect collision with food
    if snake.head.distance(food) < 16:
        scoreboard.increase_score()
        food.place_another_food()
        snake.extend_snake_body()

    # Detect collision with food
    if snake.head.xcor() < -300 or snake.head.xcor() > 280 or snake.head.ycor() < -280 or snake.head.ycor() > 250:
        scoreboard.reset()
        snake.reset()

    for segment in snake.snake_segments[1:]:
        if snake.head.distance(segment) < 12:
            scoreboard.reset()
            snake.reset()



screen.exitonclick()
