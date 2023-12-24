import random 

rand_num = random.randint(1, 50)

def guess_number():
    is_guess_right = False
    
    guess_level = input("Enter guess level of difficulty; type 'e' for easy level or 'h' for hard level: ")
    my_guess = int(input("Enter your guess: "))
    
    while is_guess_right == False:
        counter = 10
        if guess_level == "e":
            print(f"{counter} total attempts.")
            for i in range(counter):
                counter -= 1
                if my_guess > rand_num:
                    return "Too high"
                elif my_guess < rand_num:
                    return "Too low"
                else:
                    is_guess_right = True
                    return "Numbers matched; you won!"
            print(f"You have {counter} attempts left.")
        elif guess_level == "h":
            count = 5
            print(f"{count} total attempts.")
            for i in range(count):
                counter -= 1
                print(f"You have {count} attempts left.")
                if my_guess > rand_num:
                    return "Too high"
                elif my_guess < rand_num:
                    return "Too low"
                else:
                    is_guess_right = True
                    return "Numbers match; you won!"
                
    is_continuing = input("Do you want to continue guessing? Type 'y' or 'no': ")
    if is_continuing == "y":
        guess_number()
    
        

guess_number()