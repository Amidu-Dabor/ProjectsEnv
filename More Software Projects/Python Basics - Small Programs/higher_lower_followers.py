import random
from art import logo, vs
from game_data import data



# Initialize score
score = 0

def format_data(account):
	"""Takes a user's account details and returns in a printable format."""
	account_name = account["name"]
	account_desc = account["description"]
	account_country = account["country"]

	return f"{account_name}, a {account_desc}, from {account_country}."

def check_answer(guess, a_followers, b_followers):
	"""Takes the user's guess and number of followers and returns true if guess is right, or false if wrong"""
	if a_followers > b_followers:
		return guess == "a"
	else:
		return guess == "b"


# Display logo
print(logo)

# Creates a flag indicating whether game should continue or not
game_should_continue = True

account_b = random.choice(data)

while game_should_continue:
	# Generate a random account from the game data
	account_a = account_b
	account_b = random.choice(data)
	
	# Get new account for B if A and B are the same
	while account_a == account_b:
		account_b = random.choice(data)
	
	# Printable format of user's account details
	print(f"\nCompare A: {format_data(account_a)}.\n{vs}\nCompare B: {format_data(account_b)}.\n")
	
	# Ask user for a guess
	guess = input("Who has more followers? Type 'A' or 'B': ").lower()
	
	# Get follower count of each account
	a_followers_count = account_a["follower_count"]
	b_followers_count = account_b["follower_count"]
	
	# Check if user's guess is correct
	is_correct = check_answer(guess, a_followers_count, b_followers_count)
	
	# Give user a feedback on guess
	if is_correct:
		score += 1
		print(f"\nCorrect guess, Current score: {score}.")
	else:
		game_should_continue = False
		print(f"\nWrong guess, Final score: {score}.")

