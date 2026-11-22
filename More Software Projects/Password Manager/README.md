# Password Manager (Tkinter)

A desktop app for generating strong passwords and saving logins.

## How it works

- **Generate:** creates a random password of letters, numbers and symbols, and copies it to the clipboard.
- **Add:** saves the website, username, password and date to `login_credentials.json`.
- **Search:** finds the saved login for a website.

## Tech

Python · Tkinter · json · pyperclip

## Run

```bash
pip install pyperclip
python main.py
```

> **Security note:** logins are saved as **plain, unencrypted JSON**. This is a learning project; don't use it for real passwords. `login_credentials.json` is git-ignored so saved logins are never committed. A next step would be encrypting the file with a master password (for example with the `cryptography` package).
