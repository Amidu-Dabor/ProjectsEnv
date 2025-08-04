from tkinter import *
import time
from tkinter import messagebox
import random
import pyperclip
import json
import os
from datetime import datetime

FONT = "Ariel"
data = {}
new_data = {}


def find_password():

    website = website_entry.get().title()

    if len(website) == 0:
        messagebox.showinfo(title="Error", message="Please fill in search field.")
    else:
        try:
            with open("login_credentials.json", "r") as file:
                f_data = json.load(file)
        except FileNotFoundError:
            messagebox.showinfo(title="Error", message="No data file found. Add data to create file.")
        else:
            if website in f_data:
                date_saved = f_data[website]["date"]
                site_username = f_data[website]["username"]
                site_pass = f_data[website]["password"]
                time.sleep(0.8)
                messagebox.showinfo(title=website.title(), message=f"\nDate Saved: {date_saved} \nWebsite: {website} \nEmail/Username: {site_username} \nPassword: {site_pass}")
            else:
                messagebox.showerror(title="Error", message=f"No details for this website, '{website}', found.")


def create_and_write_to_file():
    with open("login_credentials.json", mode="w") as data_file:
        global data, new_data
        website = website_entry.get()
        if os.path.exists("login_credentials.json"):
            data.update(new_data)
            time.sleep(0.3)
            json.dump(data, data_file, indent=4)
            messagebox.showinfo(title="Success", message="Credentials Saved Successfully")
        else:
            create_and_write_to_file()


def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v',
               'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
               'R',
               'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [random.choice(letters) for _ in range(random.randint(8, 10))]
    password_symbols = [random.choice(symbols) for _ in range(random.randint(2, 4))]
    password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    generated_password = "".join(password_list)
    password_entry.delete(0, END)
    password_entry.insert(0, generated_password)
    pyperclip.copy(generated_password)


def save_credentials():
    # Save entries in object format
    website = website_entry.get().title()
    current_date = datetime.now()
    date_saved = current_date.strftime("%a %d %b %Y %H:%M:%S")
    user_name = username_entry.get()
    my_password = password_entry.get()
    global new_data
    new_data = {
        website: {
            "date": date_saved,
            "username": user_name,
            "password": my_password
        }
    }

    if len(website) == 0 or len(user_name) == 0 or len(my_password) == 0:
        messagebox.showerror(title="Error", message="Please fill in the empty field(s) before proceeding.")
    elif len(user_name) > 20 or len(my_password) < 10:
        messagebox.showerror(title="Error", message="Username must be less than or equal to 20 characters. \nPassword "
                                                    "must not be less than 10 characters.")
    else:
        is_proceed = messagebox.askokcancel(title=website,
                                            message=f"YOUR CREDENTIALS \n\nEmail/Username: {user_name} \nPassword: {my_password} \n\nIs it okay to proceed?")

        if is_proceed:
            try:
                with open("login_credentials.json", mode="r") as data_file:
                    global data
                    data = json.load(data_file)
            except FileNotFoundError:
                create_and_write_to_file()
            else:
                create_and_write_to_file()
            finally:
                website_entry.delete(0, END)
                password_entry.delete(0, END)


window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

canvas = Canvas(width=200, height=200)
password_icon = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=password_icon)
canvas.grid(column=1, row=0)

# Website
website_name = Label(text="Website", font=(FONT, 14))
website_name.grid(column=0, row=1)

website_entry = Entry(width=23)
website_entry.focus()
website_entry.grid(column=1, row=1)

# Search button
search = Button(text="Search", pady=2, width=3, command=find_password)
search.grid(column=2, row=1)

# Email/Username
username = Label(text="Email/Username", font=(FONT, 14))
username.grid(column=0, row=2)

username_entry = Entry(width=30)
username_entry.insert(0, "adabor@usiu.ac.ke")
username_entry.grid(column=1, row=2, columnspan=2)

# Password
password = Label(text="Password", font=(FONT, 14))
password.grid(column=0, row=3)

password_entry = Entry(width=23)
password_entry.grid(column=1, row=3)

# Save password button
save_password = Button(text="Save", pady=2, command=save_credentials)
save_password.grid(column=2, row=3)

# Generate password button
generate_pass = Button(text="Generate/Copy Password to Clipboard", width=27, pady=2, command=generate_password)
generate_pass.grid(column=1, row=4, columnspan=2)




window.mainloop()
