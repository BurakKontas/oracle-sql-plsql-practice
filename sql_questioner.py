import tkinter as tk
from tkinter import messagebox, ttk
import json
import oracledb
from PIL import Image, ImageTk

class SQLQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Soru Çözme Uygulaması")
        self.root.geometry("1200x1000")

        # Database connection defaults
        self.db_config = {
            "username": "username",
            "password": "password",
            "dsn": "connection_string"  # e.g., "localhost:1521/orcl"
        }
        
        # Load questions
        with open("sql_questions_combined.json", "r", encoding="utf-8") as f:
            self.questions = json.load(f)
        
        self.load_db_config()
        self.index = 0
        self.correct_result_cache = None
        self.hint_visible = False
        
        self.create_menu()
        self.create_ui()
        self.load_question()

    def load_db_config(self):
        try:
            with open("db_config.json", "r") as f:
                self.db_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_db_config()

    def save_db_config(self):
        with open("db_config.json", "w") as f:
            json.dump(self.db_config, f)

    def connect_db(self):
        try:
            connection = oracledb.connect(
                user=self.db_config["username"],
                password=self.db_config["password"],
                dsn=self.db_config["dsn"]
            )
            return connection
        except Exception as e:
            messagebox.showerror("DB Connection Error", str(e))
            return None

    def run_query(self, sql):
        conn = self.connect_db()
        if not conn:
            return None, "Could not connect to database"
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [col[0].lower() for col in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            cursor.close()
            conn.close()
            return result, None
        except Exception as e:
            conn.close()
            return None, str(e)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Database Connection Settings", 
                                command=self.show_connection_dialog)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)

    def show_connection_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Database Connection Settings")
        dialog.geometry("400x250")

        tk.Label(dialog, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        username_entry = tk.Entry(dialog)
        username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        username_entry.insert(0, self.db_config["username"])

        tk.Label(dialog, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        password_entry = tk.Entry(dialog, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        password_entry.insert(0, self.db_config["password"])

        tk.Label(dialog, text="DSN (host:port/service):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        dsn_entry = tk.Entry(dialog)
        dsn_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        dsn_entry.insert(0, self.db_config["dsn"])

        def save_connection():
            self.db_config = {
                "username": username_entry.get(),
                "password": password_entry.get(),
                "dsn": dsn_entry.get()
            }
            self.save_db_config()
            messagebox.showinfo("Success", "Connection settings saved!")
            dialog.destroy()

        save_btn = tk.Button(dialog, text="Save", command=save_connection)
        save_btn.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        test_btn = tk.Button(dialog, text="Test Connection", command=lambda: self.test_connection(
            username_entry.get(),
            password_entry.get(),
            dsn_entry.get()
        ))
        test_btn.grid(row=3, column=0, padx=5, pady=10, sticky="w")

    def test_connection(self, username, password, dsn):
        try:
            connection = oracledb.connect(
                user=username,
                password=password,
                dsn=dsn
            )
            connection.close()
            messagebox.showinfo("Success", "Successfully connected to database!")
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            return False

    def create_ui(self):
        # Top frame (question navigation)
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill=tk.X)

        tk.Label(top_frame, text=f"Go to Question (1-{len(self.questions)}):").pack(side=tk.LEFT, padx=5)
        self.jump_entry = tk.Entry(top_frame, width=5)
        self.jump_entry.pack(side=tk.LEFT)
        self.jump_btn = tk.Button(top_frame, text="Go", command=self.jump_to_question)
        self.jump_btn.pack(side=tk.LEFT, padx=5)

        # Title
        self.title_label = tk.Label(self.root, text="", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Hint area
        self.hint_frame = tk.Frame(self.root)
        self.hint_frame.pack(pady=5)
        self.hint_btn = tk.Button(self.hint_frame, text="Show Hint", command=self.toggle_hint)
        self.hint_btn.pack()
        self.hint_label = tk.Label(self.hint_frame, text="", font=("Arial", 12), fg="blue", wraplength=1000, justify="left")

        # SQL input
        self.sql_text = tk.Text(self.root, width=100, height=8, font=("Consolas", 12))
        self.sql_text.pack(pady=10)

        # Control buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.schema_btn = tk.Button(btn_frame, text="Show Schema", command=self.show_schema)
        self.schema_btn.grid(row=0, column=0, padx=5)
        
        self.check_btn = tk.Button(btn_frame, text="Check Answer", command=self.check_answer)
        self.check_btn.grid(row=0, column=1, padx=5)
        
        self.next_btn = tk.Button(btn_frame, text="Next Question", command=self.next_question)
        self.next_btn.grid(row=0, column=2, padx=5)

        # Result areas
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Correct result
        correct_frame = tk.Frame(result_frame)
        correct_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        tk.Label(correct_frame, text="Correct Query Result:").pack(anchor="w")
        correct_result_container = tk.Frame(correct_frame)
        correct_result_container.pack(fill=tk.BOTH, expand=True)
        
        self.correct_rownum = tk.Listbox(correct_result_container, width=4, activestyle='none',
                                        font=("Consolas", 10), bg="#f0f0f0", fg="gray")
        self.correct_rownum.pack(side=tk.LEFT, fill=tk.Y)
        
        correct_tree_scroll = tk.Scrollbar(correct_result_container, orient=tk.VERTICAL)
        correct_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.correct_tree = ttk.Treeview(correct_result_container, yscrollcommand=correct_tree_scroll.set)
        self.correct_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        correct_tree_scroll.config(command=self._scroll_both_correct)
        self.correct_rownum.config(yscrollcommand=self._scroll_both_correct)
        self.correct_tree.bind("<MouseWheel>", self._on_mousewheel_correct)
        self.correct_rownum.bind("<MouseWheel>", self._on_mousewheel_correct)

        # User result
        user_frame = tk.Frame(result_frame)
        user_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        tk.Label(user_frame, text="User Query Result:").pack(anchor="w")
        user_result_container = tk.Frame(user_frame)
        user_result_container.pack(fill=tk.BOTH, expand=True)
        
        self.user_rownum = tk.Listbox(user_result_container, width=4, activestyle='none',
                                    font=("Consolas", 10), bg="#f0f0f0", fg="gray")
        self.user_rownum.pack(side=tk.LEFT, fill=tk.Y)
        
        user_tree_scroll = tk.Scrollbar(user_result_container, orient=tk.VERTICAL)
        user_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_tree = ttk.Treeview(user_result_container, yscrollcommand=user_tree_scroll.set)
        self.user_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        user_tree_scroll.config(command=self._scroll_both_user)
        self.user_rownum.config(yscrollcommand=self._scroll_both_user)
        self.user_tree.bind("<MouseWheel>", self._on_mousewheel_user)
        self.user_rownum.bind("<MouseWheel>", self._on_mousewheel_user)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def show_schema(self):
        try:
            # Open PNG file
            image = Image.open("schema.png")
            
            # Create new window
            schema_window = tk.Toplevel(self.root)
            schema_window.title("Database Schema")
            
            # Convert image to Tkinter format
            photo = ImageTk.PhotoImage(image)
            
            # Get image dimensions and set window size
            width, height = image.size
            schema_window.geometry(f"{width}x{height}")
            
            # Display image
            label = tk.Label(schema_window, image=photo)
            label.image = photo  # Keep reference
            label.pack()
            
            # Center window
            self.center_window(schema_window)
            
        except FileNotFoundError:
            messagebox.showerror("Error", "schema.png file not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Error showing schema: {str(e)}")

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _scroll_both_correct(self, *args):
        self.correct_tree.yview(*args)
        self.correct_rownum.yview(*args)

    def _on_mousewheel_correct(self, event):
        self.correct_tree.yview("scroll", int(-1*(event.delta/120)), "units")
        self.correct_rownum.yview("scroll", int(-1*(event.delta/120)), "units")
        return "break"

    def _scroll_both_user(self, *args):
        self.user_tree.yview(*args)
        self.user_rownum.yview(*args)

    def _on_mousewheel_user(self, event):
        self.user_tree.yview("scroll", int(-1*(event.delta/120)), "units")
        self.user_rownum.yview("scroll", int(-1*(event.delta/120)), "units")
        return "break"

    def toggle_hint(self):
        self.hint_btn.pack_forget()
        current_question = self.questions[self.index]
        self.hint_label.config(text=current_question.get("hint", "No hint available for this question."))
        self.hint_label.pack()

    def jump_to_question(self):
        val = self.jump_entry.get().strip()
        if not val.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid number.")
            return
        idx = int(val) - 1
        if idx < 0 or idx >= len(self.questions):
            messagebox.showwarning("Invalid Question", f"Please enter a number between 1 and {len(self.questions)}.")
            return
        self.index = idx
        self.load_question()

    def load_question(self):
        q = self.questions[self.index]
        self.title_label.config(text=f"{q['title']}")

        self.hint_label.pack_forget()
        self.hint_btn.pack()

        self.sql_text.delete("1.0", tk.END)
        self.clear_treeview(self.correct_tree)
        self.clear_treeview(self.user_tree)
        self.correct_rownum.delete(0, tk.END)
        self.user_rownum.delete(0, tk.END)
        self.status_label.config(text="")
        self.correct_result_cache = None

        correct_sql = q["sql"]
        correct_res, corr_err = self.run_query(correct_sql)
        if corr_err:
            messagebox.showerror("Query Error (Correct SQL)", corr_err)
        else:
            self.correct_result_cache = correct_res
            self.fill_treeview(self.correct_tree, correct_res)
            self.fill_row_numbers(self.correct_rownum, len(correct_res))

    def clear_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def fill_treeview(self, tree, data):
        self.clear_treeview(tree)
        if not data:
            return
        columns = list(data[0].keys())
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='w')
        for row in data:
            tree.insert("", tk.END, values=[row[col] for col in columns])

    def fill_row_numbers(self, listbox, count):
        listbox.delete(0, tk.END)
        for i in range(1, count+1):
            listbox.insert(tk.END, str(i))

    def compare_results(self, user_res, correct_res):
        if user_res is None or correct_res is None:
            return False
        
        # Compare ignoring column names and order
        user_values = [frozenset(row.values()) for row in user_res]
        correct_values = [frozenset(row.values()) for row in correct_res]
        
        return sorted(user_values) == sorted(correct_values)

    def check_answer(self):
        user_sql = self.sql_text.get("1.0", tk.END).strip()
        if not user_sql:
            messagebox.showwarning("Warning", "Please write an SQL query.")
            return

        if self.correct_result_cache is None:
            messagebox.showerror("Error", "Correct result not available, please refresh.")
            return

        user_res, user_err = self.run_query(user_sql)
        if user_err:
            messagebox.showerror("Query Error (User SQL)", user_err)
            return

        self.fill_treeview(self.user_tree, user_res)
        self.fill_row_numbers(self.user_rownum, len(user_res))

        if self.compare_results(user_res, self.correct_result_cache):
            self.status_label.config(text="Congratulations! Correct answer.", fg="green")
        else:
            self.status_label.config(text="Wrong answer, please try again.", fg="red")

    def next_question(self):
        self.index = (self.index + 1) % len(self.questions)
        self.load_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLQuizApp(root)
    root.mainloop()