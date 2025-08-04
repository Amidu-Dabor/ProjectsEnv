from tkinter import *
import pandas as pd
import random

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
words_to_learn = {}

try:
    data = pd.read_csv("data/words_to_learn.csv")
except FileNotFoundError:
    original_data = pd.read_csv("data/french_words.csv")
    words_to_learn = original_data.to_dict(orient="records")
else:
    words_to_learn = data.to_dict(orient="records")


def next_card():
    global current_card, flip_timer
    # Cancel flip timer running in background
    window.after_cancel(flip_timer)

    current_card = random.choice(words_to_learn)
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")
    canvas.itemconfig(card_current_background_img, image=card_front_img)

    # Start a new flip timer
    window.after(4000, func=flip_card)


def flip_card():
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")
    canvas.itemconfig(card_current_background_img, image=card_back_img)


def is_known():
    words_to_learn.remove(current_card)
    words_data = pd.DataFrame(words_to_learn)
    words_data.to_csv("data/words_to_learn.csv", index=False)

    next_card()


window = Tk()
window.title("Study with Flash Cards")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

# Flip card every 5 seconds
flip_timer = window.after(4000, func=flip_card)

canvas = Canvas(width=800, height=526)

# Create the card front image
card_front_img = PhotoImage(file="images/card_front.png")
card_back_img = PhotoImage(file="images/card_back.png")
card_current_background_img = canvas.create_image(400, 263, image=card_front_img)

card_title = canvas.create_text(400, 150, text="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Ariel", 60, "bold"))

canvas.itemconfig(card_title, fill="black")
canvas.itemconfig(card_word, fill="black")
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(column=0, row=0, columnspan=2)

wrong_icon = PhotoImage(file="images/wrong.png")
unknown_button = Button(image=wrong_icon, highlightthickness=0, command=next_card)
unknown_button.grid(column=0, row=1)

check_icon = PhotoImage(file="images/right.png")
known_button = Button(image=check_icon, highlightthickness=0, command=is_known)
known_button.grid(column=1, row=1)

next_card()

window.mainloop()
