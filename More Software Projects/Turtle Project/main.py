from turtle import Turtle, Screen

# timmy = Turtle()
# print(timmy)
# timmy.shape('turtle')
# timmy.color("red", "DarkOrchid")
# timmy.color()
# timmy.forward(100)
# timmy.right(90)
# timmy.forward(100)
# timmy.right(90)
# timmy.forward(200)
# timmy.right(90)
# timmy.forward(100)
# timmy.left(110)
# timmy.forward(120)

# my_screen = Screen()
# print(my_screen.canvheight)
# my_screen.exitonclick()


from prettytable import PrettyTable

table = PrettyTable()
table.add_column('Pokemon Name', ['Pikachu', 'Squirtle', 'Charmander'])
table.add_column('Type', ['Electric', 'Water', 'Fire'])
table.junction_char = '*'
table.padding_width = 6
table.header_style = 'upper'

print(table)
