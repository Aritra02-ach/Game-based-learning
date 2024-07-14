import tkinter as tk
from tkinter import messagebox
import mysql.connector
import json
import random

# Initialize the database
def init_db():
    conn = mysql.connector.connect(host="localhost", user="root", passwd="sql123", database="learning_app")

    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(255) NOT NULL)")
    c.execute(" CREATE TABLE IF NOT EXISTS progress (user_id INTEGER,module TEXT,score INTEGER,FOREIGN KEY(user_id) REFERENCES users(id))")
    conn.commit()
    conn.close()

# Main application class
class LearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game-Based Learning App")
        self.username = None
        self.user_id = None

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Enter your username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Button(self.root, text="Start", command=self.start_app).pack()

    def start_app(self):
        self.username = self.username_entry.get()
        if not self.username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return
        self.user_id = self.get_user_id(self.username)
        self.create_main_menu()

    def get_user_id(self, username):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="sql123",
            database="learning_app"
        )
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = %s', (username,))
        user = c.fetchone()
        if user:
            user_id = user[0]
        else:
            c.execute('INSERT INTO users (username) VALUES (%s)', (username,))
            user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id

    def create_main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.username}").pack()
        tk.Button(self.root, text="Coding Module", command=self.start_coding_module).pack()
        tk.Button(self.root, text="Language Module", command=self.start_language_module).pack()
        tk.Button(self.root, text="View Progress", command=self.view_progress).pack()

    def start_coding_module(self):
        CodingModule(self.root, self.user_id,app)

    def start_language_module(self):
        LanguageModule(self.root, self.user_id,app)

    def view_progress(self):
        ProgressTracker(self.root, self.user_id,app)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Coding module class
class CodingModule:
    def __init__(self, root, user_id,app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.load_questions()
        self.create_question_screen()

    def load_questions(self):
        with open('coding_questions.json') as f:
            self.questions = json.load(f)
        self.current_question = random.choice(self.questions)

    def create_question_screen(self):
        self.clear_screen()
        tk.Label(self.root, text=self.current_question['question']).pack()
        self.answer_entry = tk.Entry(self.root)
        self.answer_entry.pack()
        tk.Button(self.root, text="Submit", command=self.check_answer).pack()
        tk.Button(self.root, text="Back to Main Menu", command=self.go_back).pack()

    def check_answer(self):
        answer = self.answer_entry.get()
        if answer.lower() == self.current_question['answer'].lower():
            messagebox.showinfo("Correct", "Correct Answer!")
            self.update_progress(10)
        else:
            messagebox.showwarning("Incorrect", "Try Again!")
        self.load_questions()
        self.create_question_screen()

    def update_progress(self, score):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="sql123",
            database="learning_app"
        )
        c = conn.cursor()
        c.execute('INSERT INTO progress (user_id, module, score) VALUES (%s, %s, %s)',
                  (self.user_id, 'Coding', score))
        conn.commit()
        conn.close()

    def go_back(self):
        self.app.create_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Language module class
class LanguageModule(CodingModule):  # Inherits from CodingModule for simplicity
    def load_questions(self):
        with open('language_questions.json') as f:
            self.questions = json.load(f)
        self.current_question = random.choice(self.questions)

    def update_progress(self, score):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="sql123",
            database="learning_app"
        )
        c = conn.cursor()
        c.execute('INSERT INTO progress (user_id, module, score) VALUES (%s, %s, %s)',
                  (self.user_id, 'Language', score))
        conn.commit()
        conn.close()

# Progress tracker class
class ProgressTracker:
    def __init__(self, root, user_id, app):
        self.root = root
        self.user_id = user_id
        self.app = app
        self.show_progress()

    def show_progress(self):
        self.clear_screen()
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="sql123",
            database="learning_app"
        )
        c = conn.cursor()
        c.execute('SELECT module, SUM(score) FROM progress WHERE user_id = %s GROUP BY module', (self.user_id,))
        rows = c.fetchall()
        conn.close()

        tk.Label(self.root, text="Your Progress:").pack()
        for row in rows:
            module, score = row
            tk.Label(self.root, text=f"{module}: {score} points").pack()
        tk.Button(self.root, text="Back to Main Menu", command=self.go_back).pack()

    def go_back(self):
        self.app.create_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# Initialize database and start the app
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LearningApp(root)
    root.mainloop()
