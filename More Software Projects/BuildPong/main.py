from turtle import Screen
from paddles import Paddles
from ball import Ball
from scoreboard import Scoreboard
import time

screen = Screen()
screen.setup(width=800, height=600)
screen.bgcolor("black")
screen.title("Pong Game")
screen.tracer(0)


left_paddle = Paddles((-360, 0))
right_paddle = Paddles((360, 0))
ball = Ball()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(left_paddle.up, "w")
screen.onkey(left_paddle.down, "s")
screen.onkey(right_paddle.up, "Up")
screen.onkey(right_paddle.down, "Down")

counter = 0
game_is_on = True
while game_is_on:
    time.sleep(ball.ball_speed)
    screen.update()
    ball.move_ball()

    # Detect collision with wall and bounce from any direction
    if ball.ycor() > (screen.window_height() / 2) - 20 or ball.ycor() < (-(screen.window_height() / 2) + 20):
        ball.bounce_y()

    # Detect collision with left or right paddle
    if ball.distance(right_paddle) < 50 and ball.xcor() > (screen.window_width() / 2) - 63 or ball.distance(left_paddle) < 50 and ball.xcor() < (-screen.window_width() / 2) + 63:
        ball.bounce_x()

    # Detect and increase score on the left when the right paddle misses the ball or when the ball goes out of bounds
    if ball.xcor() > (screen.window_width() / 2) + 10:
        scoreboard.left_score()
        ball.reset_position()

    # Detect and increase score on the right when the left paddle misses the ball or when the ball goes out of bounds
    if ball.xcor() < -(screen.window_width() / 2) - 10:
        scoreboard.right_score()
        ball.reset_position()



screen.exitonclick()
