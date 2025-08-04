from tkinter import *
import math

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 30
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
work_repetition = 0
active_timer = None
count_min = 0
count_sec = 0


# ---------------------------- TIMER RESET ------------------------------- #

# ---------------------------- TIMER MECHANISM ------------------------------- # 

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 

# ---------------------------- UI SETUP ------------------------------- #

def reset_timer():
    global work_repetition

    window.after_cancel(active_timer)
    canvas.itemconfig(timer_text, text="00:00")
    work_repetition = 0
    timer_title.config(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 45, "bold"))
    check_mark.config(text="", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 30))


def start_timer():
    global work_repetition
    work_repetition += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if work_repetition % 8 == 0:
        count_down(long_break_sec)
        timer_title.config(text="On break.", fg=RED)
    elif work_repetition % 2 == 0:
        count_down(short_break_sec)
        timer_title.config(text="On break.", fg=PINK)
    else:
        count_down(work_sec)
        timer_title.config(text="Work Time", fg=GREEN)


def count_down(minutes_in_seconds):
    count_min = math.floor(minutes_in_seconds / 60)
    count_sec = minutes_in_seconds % 60

    if count_sec < 10:
        count_sec = f"0{count_sec}"

    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if minutes_in_seconds > 0:
        global active_timer
        active_timer = window.after(1000, count_down, minutes_in_seconds - 1)
    else:
        start_timer()
        chk_marks = ""
        work_sessions = math.floor(work_repetition / 2)

        for _ in range(work_sessions):
            chk_marks += "✔"
        check_mark.config(text=chk_marks)


window = Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

timer_title = Label(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 45, "bold"))
timer_title.grid(column=1, row=0)

canvas = Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 132, text=f"00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1)

# count_down(5)

start_btn = Button(text="Start", font=(FONT_NAME, 14), bg=YELLOW, highlightthickness=0, command=start_timer)
start_btn.grid(column=0, row=2)

reset_btn = Button(text="Reset", font=(FONT_NAME, 14), bg=YELLOW, highlightthickness=0, command=reset_timer)
reset_btn.grid(column=2, row=2)

check_mark = Label(text="", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 30))
check_mark.grid(column=1, row=3)








window.mainloop()
