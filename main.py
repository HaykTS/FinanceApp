import tkinter as tk
from tkinter import ttk
import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return {"balance": 0.0}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"balance": 0.0}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinanceApp")
        self.data = load_data()
        self.setup_ui()
    def setup_ui(self):
        self.balance_label = ttk.Label(self.root, text="", font=("Consolas", 18))
        self.balance_label.pack(pady=5)
        add_button = tk.Button(self.root, text="Add 100$", font=("Consolas", 12), command=self.add_money)
        add_button.pack(pady=5)
        self.update_balance()
    def update_balance(self):
        self.balance_label.config(text=f"Balance: {self.data['balance']} $")
    def add_money(self):
        self.data['balance'] += 100
        save_data(self.data)
        self.update_balance()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()