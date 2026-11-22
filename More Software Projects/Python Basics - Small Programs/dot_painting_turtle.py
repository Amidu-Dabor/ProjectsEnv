import random
import colorgram
import turtle as t

tim = t.Turtle()
t.colormode(255)
tim.resizemode('user')

# colours = ["CadetBlue", "red", "blue", "DarkOrchid", "Orange", "aquamarine", "DarkViolet", "DarkRed", "cyan2",
#            "chocolate", "chartreuse1"]

colours = colorgram.extract('image.jpg', 10)
list_of_colours = []

# def extract_colours():
#     for colr in colours:
#         r = colr.rgb.r
#         g = colr.rgb.g
#         b = colr.rgb.b
#         # h = colr.hsl.h
#         # s = colr.hsl.s
#         # l = colr.hsl.l
#         # proportion = colr.proportion
#         image_colours = r, g, b
#         list_of_colours.append(image_colours)
#     return list_of_colours


new_colours = [(144, 74, 52), (169, 152, 45), (58, 92, 119), (224, 203, 131), (136, 162, 180), (131, 34, 26),
               (51, 117, 89), (199, 94, 72), (143, 25, 30), (18, 97, 74), (69, 47, 40), (173, 146, 153),
               (150, 177, 152), (131, 70, 74), (56, 43, 46), (237, 174, 163), (184, 88, 94), (38, 58, 71), (28, 82, 89),
               (182, 204, 178), (242, 156, 160), (93, 144, 124), (20, 66, 57), (36, 65, 96), (108, 125, 154),
               (103, 137, 147), (181, 190, 209), (74, 65, 49), (176, 198, 202)]

tim.pen(fillcolor="#000", pencolor='#000', speed=9, stretchfactor=(1.2, 1.2))
east = 0
north = 90
west = 180
south = 270

tim.hideturtle()
tim.penup()
tim.setheading(225)
tim.forward(350)
tim.setheading(0)


def draw_dots():
    for dot_count in range(1, 101):
        random_colours = random.choice(new_colours)
        tim.dot(20, random_colours)
        tim.forward(50)

        if dot_count % 10 == 0:
            tim.setheading(north)
            tim.forward(50)
            tim.setheading(west)
            tim.forward(500)
            tim.setheading(east)


draw_dots()

print(tim.pos())
screen = t.Screen()

print(screen.window_height())
print(screen.window_width())

screen.exitonclick()
