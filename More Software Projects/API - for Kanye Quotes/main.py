from tkinter import *
import requests

API_URL = "https://api.kanye.rest"


def api():
    response = requests.get(url=API_URL)
    response.raise_for_status()
    quote = response.json()["quote"]
    return quote


def get_quote():
    canvas.itemconfig(quote_text, text=api())


def initial_quote():
    return api()


window = Tk()
window.title("Kanye Says...")
window.config(padx=50, pady=50)

canvas = Canvas(width=300, height=414)

background_img = PhotoImage(file="background.png")
canvas.create_image(150, 207, image=background_img)

quote_text = canvas.create_text(150, 207, text=initial_quote(), width=250, font=("Arial", 22, "bold"), fill="white")
canvas.grid(row=0, column=0)

kanye_img = PhotoImage(file="kanye.png")
kanye_button = Button(image=kanye_img, highlightthickness=0, command=get_quote)
kanye_button.grid(row=1, column=0)

window.mainloop()
