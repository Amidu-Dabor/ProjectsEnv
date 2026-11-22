alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


def caesar(text, shift, command):
	end_text = ""
	if command == "decode":
			shift *= -1
	for char in text:
		if char in alphabet:
			char_position = alphabet.index(char)
			new_position = char_position + shift
			end_text += alphabet[new_position]
		else:
			end_text += char
	
	print(f"The {command}d message is: {end_text}.\n")
	
is_going_again = True
while is_going_again:
	command = input("\nType 'encode' to encrypt, type 'decode' to decrypt:\n").lower()
	text = input("\nType your message:\n")
	shift = int(input("Type the shift number:\n"))
	shift %= 25
	
	caesar(text=text, shift=shift, command=command)

	consent = input("Going again on Caesar Cipher? Type 'yes' or 'no': ").lower()

	if consent == "yes":
		continue
	elif consent == "no":
		is_going_again = False
	else:
		print("\nInvalid command; type either 'yes' or 'no' to give your consent.")
		continue

