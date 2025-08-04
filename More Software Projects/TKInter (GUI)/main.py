from tkinter import *


def convert():
    m_input = float(mile_input.get()) * 1.609344
    result = output_km.config(text=f"{round(m_input)}")
    return result


# Creating the screen or window
window = Tk()
window.title("Mile to Km Converter")
window.minsize(width=500, height=300)
window.config(padx=20, pady=50)

# Creating label
lbl_mile = Label(text="Enter Miles", font=("Arial", 16))
lbl_mile.grid(column=0, row=1)

mile_input = Entry(width=10)
mile_input.insert(END, "0")
mile_input.focus()
mile_input.get()
mile_input.grid(column=1, row=1)

mile_unit = Label(text="miles", font=("Arial", 12))
mile_unit.grid(column=2, row=1)

mile_equiv = Label(text="Equivalence (km):", font=("Arial", 16))
mile_equiv.grid(column=0, row=2)

output_km = Label(text="", font=("Arial", 16, "bold"))
output_km.grid(column=1, row=2)

km_unit = Label(text="km", font=("Arial", 12))
km_unit.grid(column=2, row=2)

button = Button(text="Convert", command=convert)
button.grid(column=1, row=3)




















window.mainloop()
