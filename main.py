'''

                            Online Python Compiler.
                Code, Compile, Run and Debug python program online.
Write your code in this editor and press "Run" button to execute it.

'''

import sqlite3
import hashlib
import os
from datetime import datetime

# Database Setup
DB_FILE = "finance_manager.db"

def delete_db():
    """Deletes the old database if it exists."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    print("Old database deleted.")

def init_db():
    """Initializes the database with necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # User table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    # Transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                        category TEXT,
                        amount REAL NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Budget table (make sure the 'amount' column is defined here)
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()

# Helper Functions
def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Authenticates the user by checking the username and password."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user[1] == hash_password(password):
        return user[0]
    return None

# User Registration and Login
def register():
    """Registers a new user with a unique username and password."""
    username = input("Enter a unique username: ")
    password = input("Enter a password: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    conn.close()

def login():
    """Logs in the user by checking the username and password."""
    username = input("Username: ")
    password = input("Password: ")
    user_id = authenticate(username, password)
    if user_id:
        print("Login successful!")
        return user_id
    else:
        print("Invalid credentials.")
        return None

# Income and Expense Tracking
def add_transaction(user_id):
    """Adds a new transaction (income or expense) to the database."""
    type_ = input("Enter type (income/expense): ").lower()
    category = input("Enter category (e.g., Food, Rent, Salary): ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD): ") or datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, type_, category, amount, date))
    conn.commit()
    conn.close()
    print("Transaction added successfully!")

def update_transaction(user_id):
    """Updates an existing transaction."""
    transaction_id = int(input("Enter transaction ID to update: "))
    type_ = input("Enter new type (income/expense): ").lower()
    category = input("Enter new category: ")
    amount = float(input("Enter new amount: "))
    date = input("Enter new date (YYYY-MM-DD): ") or datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''UPDATE transactions SET type = ?, category = ?, amount = ?, date = ?
                      WHERE id = ? AND user_id = ?''', (type_, category, amount, date, transaction_id, user_id))
    conn.commit()
    conn.close()
    print("Transaction updated successfully!")

def delete_transaction(user_id):
    """Deletes a transaction."""
    transaction_id = int(input("Enter transaction ID to delete: "))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
    conn.commit()
    conn.close()
    print("Transaction deleted successfully!")

# Financial Reports
def generate_report(user_id):
    """Generates a financial report for the user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT strftime('%Y-%m', date) AS month, 
                             SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
                             SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense
                      FROM transactions WHERE user_id = ? GROUP BY month''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    print("Monthly Financial Report:")
    for row in rows:
        print(f"Month: {row[0]}, Income: {row[1]}, Expense: {row[2]}, Savings: {row[1] - row[2]}")

# Budgeting
def set_budget(user_id):
    """Sets a budget for a category."""
    category = input("Enter category to set budget for: ")
    amount = float(input("Enter budget amount: "))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)", (user_id, category, amount))
    conn.commit()
    conn.close()
    print("Budget set successfully!")

def check_budget(user_id):
    """Checks the budget for different categories."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT b.category, b.amount, 
                             SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) AS spent
                      FROM budgets b 
                      LEFT JOIN transactions t ON b.user_id = t.user_id AND b.category = t.category
                      WHERE b.user_id = ?
                      GROUP BY b.category''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    print("Budget Report:")
    for row in rows:
        print(f"Category: {row[0]}, Budget: {row[1]}, Spent: {row[2]}, Remaining: {row[1] - row[2]}")

# Main Application
def main():
    """Runs the main application."""
    delete_db()  # Delete the old database before reinitializing
    init_db()
    print("Welcome to Personal Finance Manager!")
    while True:
        print("\n1. Register\n2. Login\n3. Help\n4. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                while True:
                    print("\n1. Add Transaction\n2. Update Transaction\n3. Delete Transaction\n4. Generate Report\n5. Set Budget\n6. Check Budget\n7. Logout")
                    user_choice = input("Choose an option: ")
                    if user_choice == "1":
                        add_transaction(user_id)
                    elif user_choice == "2":
                        update_transaction(user_id)
                    elif user_choice == "3":
                        delete_transaction(user_id)
                    elif user_choice == "4":
                        generate_report(user_id)
                    elif user_choice == "5":
                        set_budget(user_id)
                    elif user_choice == "6":
                        check_budget(user_id)
                    elif user_choice == "7":
                        break
                    else:
                        print("Invalid option.")
        elif choice == "3":
            print("Help: This application helps you manage your personal finances by tracking income, expenses, and budgets.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if _name_ == "_main_":
    main()
