import tkinter as tk
import hashlib
from tkinter import messagebox
from tkinter import ttk
import json
import os
from datetime import datetime

USERS_DATA = "users.json"

class FinanceApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"FinanceApp - {self.user}")
        self.root.geometry("280x400")
        self.root.configure(bg="#2e2e2e")
        self.all_users = self.load_users()
        self.data = self.all_users[self.user]
        self.setup_ui()

    def load_users(self):
        if os.path.exists(USERS_DATA):
            with open(USERS_DATA, 'r', encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_user_data(self):
        self.all_users[self.user] = self.data
        with open(USERS_DATA, 'w', encoding="utf-8") as file:
            json.dump(self.all_users, file, ensure_ascii=False, indent=4)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#2e2e2e", foreground="#ffffff")
        style.configure("TButton", font=("Segoe UI", 11), padding=6, background="#444", foreground="#fff")
        style.map("TButton",
                  background=[('active', '#555')],
                  foreground=[('active', '#fff')])
        style.configure("TEntry", font=("Segoe UI", 11), fieldbackground="#444", foreground="#fff", insertcolor="#fff")

        self.balance_label = ttk.Label(self.root, text="")
        self.balance_label.pack(pady=(10, 10))

        self.amount_entry = ttk.Entry(self.root, justify="center")
        self.amount_entry.pack(pady=5)
        self.amount_entry.insert(0, "0")

        buttons_frame = tk.Frame(self.root, bg="#2e2e2e")
        buttons_frame.pack(pady=5)

        add_btn = ttk.Button(buttons_frame, text="Add", command=self.add_money)
        add_btn.grid(row=0, column=0, padx=5)

        remove_btn = ttk.Button(buttons_frame, text="Remove", command=self.remove_money)
        remove_btn.grid(row=0, column=1, padx=5)

        self.history_label = ttk.Label(self.root, text="History")
        self.history_label.pack(pady=5)

        self.history_box = tk.Listbox(self.root, height=5)
        self.history_box.pack(pady=5, fill="both")

############################################
        logout_btn = ttk.Button(self.root, text="Logout", command=self.logout)
        logout_btn.pack(pady=(10, 0))
############################################
        self.update_history()
        self.update_balance()

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.data['balance']:.2f}")

    def get_amount(self):
        try:
            amount = float(self.amount_entry.get())
            return max(0, amount)
        except ValueError:
            return 0.0

    def update_history(self):
        self.history_box.delete(0, tk.END)
        history = self.data.get("history", [])
        for h in reversed(history[-5:]):
            self.history_box.insert(tk.END, h)

    def add_money(self):
        amount = self.get_amount()
        if amount > 0:
            self.data["balance"] += amount
            self.data.setdefault("history", []).append(f"{self.timestamp()} +${amount:.2f}")
            self.save_user_data()
            self.update_balance()
            self.update_history()
        else:
            messagebox.showerror("ValueError", "Number less or equal to 0")

    def remove_money(self):
        amount = self.get_amount()
        if amount > self.data['balance']:
            messagebox.showerror("ValueError", "Number too big")
            return
        self.data['balance'] -= amount
        self.data.setdefault("history", []).append(f"{self.timestamp()} -${amount:.2f}")
        self.save_user_data()
        self.update_balance()
        self.update_history()

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
######################################
    def logout(self):
        self.all_users.pop("last_logged_in", None)
        with open(USERS_DATA, 'w', encoding="utf-8") as file:
            json.dump(self.all_users, file, ensure_ascii=False, indent=4)
        self.root.destroy()
        launch_authenticator()
#######################################

class Authenticator:
    def __init__(self, root):
        self.root = root
        self.root.title("Authenticate")
        self.frame = ttk.Frame(root)
        self.frame.pack(pady=5)
        ttk.Label(self.frame, text="Login").grid(row=0, column=0, sticky="e")
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1)
        ttk.Label(self.frame, text="Password").grid(row=1, column=0, sticky="e")
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1)
        ttk.Button(self.frame, text="Login", command=self.login).grid(row=2, column=0)
        ttk.Button(self.frame, text="Register", command=self.register).grid(row=2, column=1)

    def register(self):
        user_entry = self.username_entry.get().strip()
        psw_entry = self.password_entry.get().strip()

        if not user_entry or not psw_entry:
            messagebox.showerror("RegisterError", "No text inputed")
            return
        users = self.load_users()
        if user_entry in users:
            messagebox.showerror("UsersError", "User already exists")
            return
        users[user_entry] = {"password": self.hash_passwords(psw_entry), "balance": 0.0, "history": []}
        self.save_data(users)

    def login(self):
        user_entry = self.username_entry.get().strip()
        psw_entry = self.password_entry.get().strip()
        if not user_entry or not psw_entry:
            messagebox.showerror("LoginError", "No text inputed")
            return
        users = self.load_users()
        if user_entry in users and users[user_entry]["password"] == self.hash_passwords(psw_entry):
            ####################################
            users["last_logged_in"] = user_entry
            ####################################
            self.save_data(users)
            self.frame.destroy()
            FinanceApp(self.root, user_entry)
        else:
            messagebox.showerror("UserError", "User doesn't exist or password incorrect")

    def hash_passwords(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        if os.path.exists(USERS_DATA):
            with open(USERS_DATA, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self, data):
        with open(USERS_DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def launch_authenticator():
    root = tk.Tk()
    Authenticator(root)
    root.mainloop()

###########################################################
def main():
    if os.path.exists(USERS_DATA):
        with open(USERS_DATA, 'r', encoding="utf-8") as f:
            users = json.load(f)
        last_user = users.get("last_logged_in")
        if last_user and last_user in users:
            root = tk.Tk()
            FinanceApp(root, last_user)
            root.mainloop()
            return
    launch_authenticator()
###########################################################

if __name__ == "__main__":
    main()