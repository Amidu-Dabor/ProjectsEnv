# Read the names of invitees and save as a list.
with open("./Input/Names/invited_names.txt", mode="r") as names_file:
    invitees = names_file.readlines()

# Read the contents of the letter and save as strings.
with open("./Input/Letters/starting_letter.txt", mode="r") as letter:
    letter_contents = letter.read()
    # Get each name of an invitee.
    for name in invitees:
        stripped_name = name.strip()
        new_letter = letter_contents.replace("[name]", stripped_name)

        # Save the new letter for final delivery.
        with open(f"./Output/ReadyToSend/Letter-for-{stripped_name}.txt", mode="w") as letter_to_send:
            letter_to_send.write(new_letter)

