import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
 
# ==========================================
# 1. DATABASE SETUP & LOGIC
# ==========================================
DB_NAME = "budget.db"

def init_db():
    """Initializes the local SQLite database and creates the transactions table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            type TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_transaction_to_db(desc, category, amount, tx_type):
    """Inserts a verified record into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO transactions (date, description, category, amount, type) VALUES (?, ?, ?, ?, ?)",
        (date_str, desc, category, amount, tx_type)
    )
    conn.commit()
    conn.close()

def remove_transaction_from_db():
    """Removes all entries from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM transactions"
    )
    conn.commit()
    conn.close()
    refresh_ui_data()

def fetch_all_transactions():
    """Retrieves all stored rows from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, description, category, amount, type FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def calculate_balance():
    """Sums all deposits and subtracts all expenses to find the net balance."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT amount, type FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    total = 0.0
    for amount, tx_type in rows:
        if tx_type == "Deposit":
            total += amount
        else:
            total -= amount
    return total

# ==========================================
# 2. GUI INTERFACE & USER ACTIONS
# ==========================================
def handle_submit():
    """Validates user inputs, saves data, and updates the display grid."""
    desc = entry_desc.get().strip()
    category = combo_category.get()
    amount_str = entry_amount.get().strip()
    tx_type = tx_type_var.get()
    
    if not desc or not amount_str:
        messagebox.showwarning("Input Error", "Please fill out Description and Amount fields.")
        return
        
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Amount must be a positive number (e.g., 45.50).")
        return

    # Save to local database
    add_transaction_to_db(desc, category, amount, tx_type)
    
    # Reset UI input boxes
    entry_desc.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    combo_category.set("Unsorted")
    
    # Refresh visible tables
    refresh_ui_data()
    

def refresh_ui_data():
    """Clears the table layout and recalculates totals across the UI dashboard."""
    # 1. Clear old treeview items
    for item in tree.get_children():
        tree.delete(item)
        
    # 2. Populate ledger rows
    for row in fetch_all_transactions():
        tx_id, date, desc, cat, amt, t_type = row
        amt_display = f"${amt:.2f}"
        
        # Apply distinct color tags to distinguish income vs spending
        row_tag = "deposit_row" if t_type == "Deposit" else "expense_row"
        tree.insert("", tk.END, values=(date, desc, cat, amt_display, t_type), tags=(row_tag,))
        
    # 3. Recalculate financial balance display
    current_bal = calculate_balance()
    lbl_balance.config(text=f"${current_bal:.2f}")
    
    # Dynamic text coloring based on debt vs savings status
    if current_bal < 0:
        lbl_balance.config(foreground="red")
    else:
        lbl_balance.config(foreground="green")

# ==========================================
# 3. WINDOW INTERFACE INITIALIZATION
# ==========================================
init_db()

root = tk.Tk()
root.title("Desktop Ledger & Checkbook Manager")
root.geometry("750x550")
root.resizable(True, True)
root.minsize(550, 400)
root.configure(bg="#f5f5f5")

# --- TOP ROW: DASHBOARD CARD ---
frame_summary = tk.LabelFrame(root, text=" Financial Balance Account ", font=("Arial", 11, "bold"), bg="#ffffff", padx=15, pady=10)
frame_summary.pack(fill="x", padx=15, pady=10)

lbl_bal_title = tk.Label(frame_summary, text="Current Running Balance:", font=("Arial", 12), bg="#ffffff")
lbl_bal_title.pack(side="left")

lbl_balance = tk.Label(frame_summary, text="$0.00", font=("Arial", 18, "bold"), bg="#ffffff", foreground="green")
lbl_balance.pack(side="right")

# --- MIDDLE ROW: DATA INPUT PANEL ---
frame_input = tk.LabelFrame(root, text=" Log New Checkbook Transaction ", font=("Arial", 11, "bold"), bg="#f5f5f5", padx=10, pady=10)
frame_input.pack(fill="x", padx=15, pady=5)

# Entry: Description
tk.Label(frame_input, text="Description:", bg="#f5f5f5").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_desc = tk.Entry(frame_input, width=22, font=("Arial", 10))
entry_desc.grid(row=0, column=1, padx=5, pady=5)

# Entry: Category Dropdown
tk.Label(frame_input, text="Category:", bg="#f5f5f5").grid(row=0, column=2, sticky="w", padx=5, pady=5)
categories = ["Wants", "Needs", "Income"]
combo_category = ttk.Combobox(frame_input, values=categories, width=15, state="readonly")
combo_category.set("Unsorted")
combo_category.grid(row=0, column=3, padx=5, pady=5)

# Entry: Cash Amount
tk.Label(frame_input, text="Amount ($):", bg="#f5f5f5").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_amount = tk.Entry(frame_input, width=22, font=("Arial", 10))
entry_amount.grid(row=1, column=1, padx=5, pady=5)

# Entry: Radio Selection Buttons
tx_type_var = tk.StringVar(value="Expense")
rad_expense = tk.Radiobutton(frame_input, text="Expense (-)", variable=tx_type_var, value="Expense", bg="#f5f5f5")
rad_deposit = tk.Radiobutton(frame_input, text="Deposit (+)", variable=tx_type_var, value="Deposit", bg="#f5f5f5")
rad_expense.grid(row=1, column=2, sticky="w", padx=5)
rad_deposit.grid(row=1, column=3, sticky="w", padx=5)

# Action Trigger Button
btn_submit = tk.Button(frame_input, text="Save Transaction", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=handle_submit, padx=3)
btn_submit.grid(row=2, column=0, columnspan=2, pady=5) 

# Action Trigger Button
btn_submit = tk.Button(frame_input, text="Delete Ledger", bg="#AF4C4C", fg="white", font=("Arial", 10, "bold"), command=remove_transaction_from_db, padx=10)
btn_submit.grid(row=2, column=2, columnspan=2, pady=5) 

# --- BOTTOM ROW: LEDGER TABLE DISPLAY ---
frame_ledger = tk.LabelFrame(root, text=" Transaction History Ledger ", font=("Arial", 11, "bold"), bg="#f5f5f5", padx=10, pady=10)
frame_ledger.pack(fill="both", expand=True, padx=15, pady=10)

# Setting up Data Table Grid Columns
columns = ("date", "desc", "cat", "amt", "type")
tree = ttk.Treeview(frame_ledger, columns=columns, show="headings", selectmode="browse")

tree.heading("date", text="Timestamp")
tree.heading("desc", text="Description")
tree.heading("cat", text="Category")
tree.heading("amt", text="Amount")
tree.heading("type", text="Type")

tree.column("date", width=120, anchor="center")
tree.column("desc", width=200, anchor="w")
tree.column("cat", width=110, anchor="center")
tree.column("amt", width=100, anchor="e")
tree.column("type", width=90, anchor="center")

# Visual text color definitions for lists
tree.tag_configure("deposit_row", foreground="#2E7D32", background="#E8F5E9") # Subtle Green Text/Row
tree.tag_configure("expense_row", foreground="#C62828", background="#FFEBEE") # Subtle Red Text/Row

# Add a convenient scrollbar tool to the ledger layout
scrollbar = ttk.Scrollbar(frame_ledger, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- INITIAL APP BOOT DATA REFRESH ---
refresh_ui_data()

root.mainloop()