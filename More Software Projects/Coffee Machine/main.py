from menu import MenuItem
from coffee_maker import CoffeeMaker
from money_machine import MoneyMachine


menu = MenuItem()
coffee_maker = CoffeeMaker()
money_machine = MoneyMachine()


is_on = True

while is_on:
    choice = input("What would you like? (espresso/latte/cappuccino): ")
    if choice == "off":
        is_on = False
    elif choice == "report":
        coffee_maker.report()
        money_machine.report()
    else:
        drink = menu.MENU[choice]
        if coffee_maker.is_resource_sufficient(drink["ingredients"]):
            payment = money_machine.process_coins()
            if money_machine.is_transaction_successful(payment, drink["cost"]):
                coffee_maker.make_coffee(choice, drink["ingredients"])
