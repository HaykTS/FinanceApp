import tkinter as tk
import hashlib
from tkinter import ttk, messagebox, filedialog
import csv
import json
import os
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SESSION_FILE = "current_user.json"
USERS_DATA = "users.json"
CURRENT_LANG = "ru"
LANGUAGES = {
    "en": {
        "title": "FinanceApp",
        "balance": "Balance",
        "income": "Incomes",
        "expense": "Expenses",
        "add": "Add",
        "remove": "Remove",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "username": "Login",
        "password": "Password",
        "category": "Category",
        "description": "Description",
        "amount": "Amount",
        "export": "Export to CSV",
        "chart": "Chart",
        "select_language": "Language",
        "welcome": "Welcome",
        "export_success": "Report exported to:",
        "no_transactions": "No transactions to export.",
        "error_input": "No text inputted",
        "error_user_exists": "User already exists",
        "error_user_invalid": "User doesn't exist or password incorrect",
        "error_amount": "Invalid amount or exceeds balance",
        "error_fill_all": "Please fill all fields",
    },
    "ru": {
        "title": "Финансы",
        "balance": "Баланс",
        "income": "Доходы",
        "expense": "Расходы",
        "add": "Добавить",
        "remove": "Снять",
        "logout": "Выйти",
        "login": "Вход",
        "register": "Регистрация",
        "username": "Логин",
        "password": "Пароль",
        "category": "Категория",
        "description": "Описание",
        "amount": "Сумма",
        "export": "Экспорт в CSV",
        "chart": "Диаграмма",
        "select_language": "Язык",
        "welcome": "Добро пожаловать",
        "export_success": "Отчёт экспортирован в:",
        "no_transactions": "Нет операций для экспорта.",
        "error_input": "Пустой ввод",
        "error_user_exists": "Пользователь уже существует",
        "error_user_invalid": "Неверный логин или пароль",
        "error_amount": "Некорректная сумма или превышает баланс",
        "error_fill_all": "Заполните все поля",
    },
    "hy": {
        "title": "Ֆինանսներ",
        "balance": "Մնացորդ",
        "income": "Եկամուտներ",
        "expense": "Ծախսեր",
        "add": "Ավելացնել",
        "remove": "Հեռացնել",
        "logout": "Դուրս գալ",
        "login": "Մուտք",
        "register": "Գրանցվել",
        "username": "Մուտքանուն",
        "password": "Գաղտնաբառ",
        "category": "Կատեգորիա",
        "description": "Նկարագրություն",
        "amount": "Գումար",
        "export": "Արտահանել CSV",
        "chart": "Գրաֆիկ",
        "select_language": "Լեզու",
        "welcome": "Բարի գալուստ",
        "export_success": "Հաշվետվությունը արտահանվել է՝",
        "no_transactions": "Գործարքներ չկան արտահանման համար։",
        "error_input": "Դատարկ մուտքագրում",
        "error_user_exists": "Օգտատերը արդեն գոյություն ունի",
        "error_user_invalid": "Սխալ մուտքանուն կամ գաղտնաբառ",
        "error_amount": "Սխալ գումար կամ գերազանցում է մնացորդը",
        "error_fill_all": "Խնդրում ենք լրացնել բոլոր դաշտերը",
    }
}


def l(key):
    return LANGUAGES[CURRENT_LANG].get(key, key)

def create_lang_selector(parent, callback):
    frame = ttk.Frame(parent)
    frame.pack(pady=5)

    ttk.Label(frame, text=l("select_language")).pack(side="left")

    combobox = ttk.Combobox(frame, values=["en", "ru", "hy"], state="readonly")
    combobox.set(CURRENT_LANG)
    combobox.pack(padx=5)

    def on_change(event):
        global CURRENT_LANG
        CURRENT_LANG = combobox.get()
        callback()

    combobox.bind("<<ComboboxSelected>>", on_change)
    return frame

def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("username")
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


class FinanceApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"FinanceApp - {self.user}")
        create_lang_selector(self.root, lambda: [self.root.destroy(), launch_authenticator()])
        self.root.geometry("800x650")
        self.root.configure(bg="#2e2e2e")
        self.all_users = self.load_users()
        self.data = self.all_users[self.user]
        self.setup_ui()
        self.update_history()
        self.update_chart()

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
        style.configure("TLabel", font=("Segoe UI", 12), background="#2e2e2e", foreground="#ffffff")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6, background="#444", foreground="#fff")
        style.map("TButton", background=[('active', '#555')], foreground=[('active', '#fff')])
        style.configure("TEntry", font=("Segoe UI", 11), fieldbackground="#444", foreground="#fff", insertcolor="#fff")

        greeting = ttk.Label(self.root, text=f"Hello, {self.user}!", style="Header.TLabel")
        greeting.pack(pady=(10, 5))

        top_frame = tk.Frame(self.root, bg="#2e2e2e")
        top_frame.pack(pady=5)

        self.balance_label = ttk.Label(top_frame, text="", width=20, anchor="center")
        self.balance_label.grid(row=0, column=0, padx=5)

        self.income_label = ttk.Label(top_frame, text=f"{l("income")}: ${self.data.get('income', 0.0):.2f}", width=20,anchor="center")
        self.income_label.grid(row=0, column=1, padx=5)

        self.expense_label = ttk.Label(top_frame, text=f"Expensess: ${self.data.get('expense', 0.0):.2f}", width=20,anchor="center")
        self.expense_label.grid(row=0, column=2, padx=5)

        actions_frame = tk.Frame(self.root, bg="#2e2e2e")
        actions_frame.pack(pady=10)

        ttk.Button(actions_frame, text="Add Income", command=self.add_money).grid(row=0, column=0, padx=5)
        ttk.Button(actions_frame, text="Add Expense", command=self.remove_money).grid(row=0, column=1, padx=5)
        ttk.Button(actions_frame, text="Export", command=self.export_csv).grid(row=0, column=3, padx=5)

        self.amount_entry = ttk.Entry(self.root, justify="center")
        self.amount_entry.pack(pady=5)
        self.amount_entry.insert(0, "0")

        ttk.Label(self.root, text="Category").pack()
        self.category_var = tk.StringVar(value="Other")
        self.category_list = ttk.Combobox(self.root, textvariable=self.category_var, state="readonly")
        self.category_list["values"] = ["Salary", "Food", "Transportation", "Parking", "Varks", "Apariks", "Other"]
        self.category_list.pack()

        bottom_frame = tk.Frame(self.root, bg="#2e2e2e")
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = tk.Frame(bottom_frame, bg="#2e2e2e")
        left_panel.pack(side="left", expand=True, fill="both")

        right_panel = tk.Frame(bottom_frame, bg="#2e2e2e")
        right_panel.pack(side="right", expand=True, fill="both")

        ttk.Label(left_panel, text="Expenses by category").pack(pady=(0, 5))

        self.interval_var = tk.StringVar(value="All time")
        intervals = ["7 days","30 days", "All time"]
        self.interval_list = ttk.Combobox(left_panel, textvariable=self.interval_var, values=intervals, state="readonly")
        self.interval_list.pack()

        self.interval_list.bind("<<ComboboxSelected>>", lambda e: self.update_chart())

        self.fig, self.ax = plt.subplots(figsize=(4,3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=left_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Label(right_panel, text="Last Transactions").pack(pady=(0, 5))
        self.history_box = tk.Listbox(
            right_panel,
            height=5,
            bg="#3a3a3a",
            fg="white",
            selectbackground="#555555",
            highlightthickness=0,
            relief="flat"
        )

        self.history_box.pack(fill="both", expand=True)

        logout_btn = ttk.Button(self.root, text="Logout", command=self.logout)
        logout_btn.pack(pady=(10, 0))

        self.update_history()
        self.update_balance()
        self.recalc()

    def update_chart(self):
        self.ax.clear()
        self.fig.patch.set_facecolor("#2e2e2e")
        self.ax.set_facecolor("#2e2e2e")

        history = self.data.get("history", [])
        now = datetime.now()
        filtered = []
        for h in history:
            if h["type"] == "remove":
                ts = datetime.strptime(h["timestamp"], "%Y-%m-%d %H:%M:%S")
                delta = now - ts
                interval = self.interval_var.get()
                if (
                        interval == "7 days" and delta.days <= 7 or
                        interval == "30 days" and delta.days <= 30 or
                        interval == "All time"
                ):
                    filtered.append(h)

        categories = {}
        for e in filtered:
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + e["amount"]

        if not categories:
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12, color="white")
        else:
            labels = list(categories.keys())
            sizes = list(categories.values())
            self.ax.pie(sizes, labels=labels, startangle=140, autopct="%1.1f%%", textprops={'color': 'white'})

        self.ax.set_title("Expenses by category", color="white")
        self.canvas.draw()

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.data['balance']:.2f}")
    def recalc(self):
        income = 0.0
        expense = 0.0
        history = self.data.get("history", [])
        for d in history:
            if d["type"] == "add":
                income += d["amount"]
            elif d["type"] == "remove":
                expense += d["amount"]
        self.data["income"] = income
        self.data["expense"] = expense
        self.income_label.config(text=f"{l("income")}: ${income:.2f}")
        self.expense_label.config(text=f"{l("expense")}: ${expense:.2f}")

    def export_csv(self):
        history = self.data.get("history", [])
        if not history:
            messagebox.showinfo(title="ValueError", message="No history found")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV Report"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Type", "Amount", "Category"])
                for h in history:
                    writer.writerow([
                        h.get("timestamp", ""),
                        h.get("type", ""),
                        h.get("amount", ""),
                        h.get("category", "")
                    ])
            messagebox.showinfo(title="ExportSuccess", message=f"File has exported successfully to:\n {file_path}")

        except Exception as ex:
            messagebox.showerror(title="ExportError", message=str(ex))

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
            if isinstance(h, dict):
                sign = "+" if h["type"] == "add" else "-"
                text = f"[{h["timestamp"]}]  {sign} ${h["amount"]:.2f}  ({h["category"]})"
                self.history_box.insert(tk.END, text)

    def add_money(self):
        amount = self.get_amount()
        if amount > 0:
            self.data["balance"] += amount
            self.data.setdefault("history", []).append({
                "timestamp": self.timestamp(),
                "amount": amount,
                "type": "add",
                "category": self.category_var.get()
            })
            self.save_user_data()
            self.update_balance()
            self.update_history()
            self.recalc()
            self.update_chart()
        else:
            messagebox.showerror("ValueError", "Number less or equal to 0")

    def remove_money(self):
        amount = self.get_amount()
        if amount > self.data['balance']:
            messagebox.showerror("ValueError", "Number too big")
            return
        self.data['balance'] -= amount
        self.data.setdefault("history", []).append({
                "timestamp": self.timestamp(),
                "amount": amount,
                "type": "remove",
                "category": self.category_var.get()
            })
        self.save_user_data()
        self.update_balance()
        self.update_history()
        self.recalc()
        self.update_chart()

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def logout(self):
        self.all_users.pop("last_logged_in", None)
        with open(USERS_DATA, 'w', encoding="utf-8") as file:
            json.dump(self.all_users, file, ensure_ascii=False, indent=4)
        clear_session()
        self.root.destroy()
        launch_authenticator()

class Authenticator:
    def __init__(self, root):
        self.root = root
        self.root.title("Authenticate")
        create_lang_selector(self.root, lambda: [self.root.destroy(), launch_authenticator()])
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
        users[user_entry] = {
            "password": self.hash_passwords(psw_entry),
            "balance": 0.0,
            "income": 0.0,
            "expense": 0.0,
            "history": []
        }
        self.save_data(users)

    def login(self):
        user_entry = self.username_entry.get().strip()
        psw_entry = self.password_entry.get().strip()
        if not user_entry or not psw_entry:
            messagebox.showerror("LoginError", "No text inputed")
            return
        users = self.load_users()
        if user_entry in users and users[user_entry]["password"] == self.hash_passwords(psw_entry):

            users["last_logged_in"] = user_entry
            save_session(user_entry)
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

def main():
    if os.path.exists(USERS_DATA):
        with open(USERS_DATA, 'r', encoding="utf-8") as f:
            users = json.load(f)
        last_user = users.get("last_logged_in")
        if last_user:
            root = tk.Tk()
            FinanceApp(root, last_user)
            root.mainloop()
            return


    launch_authenticator()

if __name__ == "__main__":
    main()
