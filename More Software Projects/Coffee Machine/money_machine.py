from menu import MenuItem


class MoneyMachine:
    menu = MenuItem()
    profit_made = menu.profit

    def report(self):
        print(f"Money: ${menu.profit}")

    def process_coins(self):
        """Returns the total calculated from coins inserted."""
        print("Please insert coins.")
        total = int(input("how many quarters?: ")) * 0.25
        total += int(input("how many dimes?: ")) * 0.1
        total += int(input("how many nickles?: ")) * 0.05
        total += int(input("how many pennies?: ")) * 0.01
        return total

    def is_transaction_successful(self, money_received, drink_cost):
        """Return True when the payment is accepted, or False if money is insufficient."""
        if money_received >= drink_cost:
            change = round(money_received - drink_cost, 2)
            print(f"Here is ${change} in change.")
            global profit_made
            profit_made += drink_cost
            return True
        else:
            print("Sorry that's not enough money. Money refunded.")
            return False
