from menu import MenuItem


menu = MenuItem()


class CoffeeMaker:

    def report(self):
        print(f"Water: {menu.resources['water']}ml")
        print(f"Milk: {menu.resources['milk']}ml")
        print(f"Coffee: {menu.resources['coffee']}g")

    def is_resource_sufficient(self, order_ingredients):
        """Returns True when order can be made, False if ingredients are insufficient."""
        for item in order_ingredients:
            if order_ingredients[item] > menu.resources[item]:
                print(f"Sorry there is not enough {item}.")
                return False
        return True

    def make_coffee(self, drink_name, order_ingredients):
        """Deduct the required ingredients from the resources."""
        for item in order_ingredients:
            menu.resources[item] -= order_ingredients[item]
        print(f"Here is your {drink_name} ☕️. Enjoy!")
