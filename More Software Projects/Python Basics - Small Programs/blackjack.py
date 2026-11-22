############### Blackjack Project #####################

import random


def deal_card():
	"""Returns a random card from the deck."""

	cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
	card = random.choice(cards)
	return card
	

def calculate_score(cards):
	"""Takes a list of cards and return the score calculated from the cards."""

	score = sum(cards)

	if len(cards) == 2 and sum(cards) == 21:
		return 0

	if 11 in cards and sum(cards) > 21:
		cards.remove(11)
		cards.append(1)
	
	return score


def compare(user_score, computer_score):
	"""
	Compares user_score and computer_score. If the computer and user both have the same 		score, then it's a draw. If the computer has a blackjack (0), then the user loses. If 		the user has a blackjack (0), then the user wins. If the user_score is over 21, then the 	user loses. If the computer_score is over 21, then the computer loses. If none of the 		above, then the player with the highest score wins.
	"""

	if user_score == computer_score:
		return "It's a draw."
	elif computer_score == 0:
		return "You lose; computer has Blackjack."
	elif user_score == 0:
		return "You win; you have Blackjack."
	elif user_score > 21:
		return "You lose."
	elif computer_score > 21:
		return "Computer loses."
	elif user_score > computer_score:
		return "You win."
	else:
		return "You lose."
		

def play_game():
	"""Deals the user and computer 2 cards each using deal_card() and append()."""

	user_cards = []
	computer_cards = []
	is_game_over = False
	
	for _ in range(2):
		user_cards.append(deal_card())
		computer_cards.append(deal_card())
		
	#  Call calculate_score(). If the computer or the user has a blackjack (0) or if the 		user's score is over 21, then the game ends.
	while not is_game_over:
		user_score = calculate_score(user_cards)
		computer_score = calculate_score(computer_cards)
		
		print(f"\n Your cards: {user_cards}, Current score: {user_score}")
		print(f" Computer cards: {computer_cards[0]}")
		
		if user_score == 0 or computer_score == 0 or user_score > 21:
			is_game_over = True
		else:
			add_card = input("\n Type 'y' to add another, or 'n' to end game: ")
			if add_card == "y":
				user_cards.append(deal_card())
			else:
				is_game_over = True
	
	# The computer keeps drawing cards as long as it has a score less than 17.
	while not computer_score == 0 and computer_score < 17:
		computer_cards.append(deal_card())
		computer_score = calculate_score(computer_cards)
	
	print(f"\n Your final cards: {user_cards}, Final score: {user_score}\n")
	print(f" Computer's final cards: {computer_cards}, Final score: {computer_score}\n")
	print(f" {compare(user_score, computer_score)}")


play_consent = input("\n Do you want to play Blackjack? Type 'y' to play or 'n' to reject: ")

# Clear the console and start a new game of blackjack and show the logo from art.py if a user types 'y' to play.
while play_consent == "y":
	play_game()
	
