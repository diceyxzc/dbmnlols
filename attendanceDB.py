import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import mysql.connector
from datetime import datetime

# Connection to database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="attendance_db"
)
acc = mydb.cursor()

# Backend functions
def fetch_employees():
    acc.execute("SELECT Employee_ID, First_Name, Last_Name FROM Employees")
    employees = acc.fetchall()
    return {f"{first} {last} (ID: {emp_id})": emp_id for emp_id, first, last in employees}

def time_in():
    selected = employee_combo.get()
    if not selected:
        messagebox.showerror("Error", "Please select an employee")
        return

    employee_id = employee_dict[selected]
    now = datetime.now()
    date_today = now.date()
    current_time = now.time()

    try:
        acc.execute("""
            SELECT * FROM Attendance
            WHERE Employee_ID = %s AND DATE(Attendance_Date) = %s
        """, (employee_id, date_today))
        record = acc.fetchone()

        if record:
            messagebox.showinfo("Info", "Already timed in today!")
        else:
            acc.execute("""
                INSERT INTO Attendance (Attendance_Date, Time_In, Employee_ID)
                VALUES (%s, %s, %s)
            """, (now, current_time, employee_id))
            mydb.commit()
            messagebox.showinfo("Success", "Time In recorded!")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def time_out():
    selected = employee_combo.get()
    if not selected:
        messagebox.showerror("Error", "Please select an employee")
        return

    employee_id = employee_dict[selected]
    now = datetime.now()
    date_today = now.date()
    current_time = now.time()

    try:
        acc.execute("""
            SELECT Attendance_ID FROM Attendance
            WHERE Employee_ID = %s AND DATE(Attendance_Date) = %s
        """, (employee_id, date_today))
        record = acc.fetchone()

        if record:
            attendance_id = record[0]
            acc.execute("""
                UPDATE Attendance
                SET Time_Out = %s
                WHERE Attendance_ID = %s
            """, (current_time, attendance_id))
            mydb.commit()
            messagebox.showinfo("Success", "Time Out recorded!")
        else:
            messagebox.showerror("Error", "No Time In record found for today!")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def generate_reports():
    try:
        acc.execute("""
            SELECT d.Department_Name, e.First_Name, e.Last_Name, a.Attendance_Date, a.Time_In, a.Time_Out
            FROM Attendance a
            JOIN Employees e ON a.Employee_ID = e.Employee_ID
            JOIN Departments d ON e.Department_ID = d.Department_ID
            ORDER BY a.Attendance_Date DESC
        """)
        records = acc.fetchall()

        report_window = tk.Toplevel(root)
        report_window.title("Attendance Reports")
        report_window.geometry("1000x500")

        tree = ttk.Treeview(report_window, columns=("Department", "Name", "Date", "Time In", "Time Out"), show="headings")
        tree.heading("Department", text="Department")
        tree.heading("Name", text="Employee Name")
        tree.heading("Date", text="Date")
        tree.heading("Time In", text="Time In")
        tree.heading("Time Out", text="Time Out")
        
        tree.column("Department", width=150, anchor="center")
        tree.column("Name", width=150, anchor="center")
        tree.column("Date", width=100, anchor="center")
        tree.column("Time In", width=100, anchor="center")
        tree.column("Time Out", width=100, anchor="center")


        for row in records:
            department = row[0]
            name = f"{row[1]} {row[2]}"
            date = row[3].strftime("%Y-%m-%d")
            time_in = row[4]
            time_out = row[5] if row[5] else "N/A"
            tree.insert("", tk.END, values=(department, name, date, time_in, time_out))

        tree.pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def clear_attendance():
    answer = messagebox.askyesno("Confirm", "Are you sure you want to clear all attendance records?")
    if answer:
        try:
            acc.execute("DELETE FROM Attendance")
            mydb.commit()
            messagebox.showinfo("Success", "All attendance records cleared!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# Main GUI window
root = tk.Tk()
root.title("Accutime Attendance System")
root.geometry("600x420")
root.configure(bg="#1e1e2f")

# Modern theme colors
PRIMARY_COLOR = "#3e8ef7"
BG_COLOR = "#1e1e2f"
CARD_COLOR = "#2c2f4a"
TEXT_COLOR = "#ffffff"

# Style Configuration
style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background=BG_COLOR)
style.configure("TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 12))
style.configure("TButton", background=PRIMARY_COLOR, foreground='white', font=("Segoe UI", 11, "bold"), padding=6)
style.configure("TCombobox", font=("Segoe UI", 11), padding=4)

style.map("TButton",
          background=[('active', '#5aa9fb')],
          foreground=[('disabled', '#d3d3d3')])

# Top Frame
frame_top = ttk.Frame(root, padding=20, style="TFrame")
frame_top.pack(fill=tk.X, padx=20, pady=10)

title = ttk.Label(frame_top, text="ACCUTIME ATTENDANCE SYSTEM", font=("Segoe UI", 16, "bold"), anchor="center", style="TLabel")
title.pack(pady=(0, 10), fill=tk.X)

employee_section = ttk.Frame(frame_top, style="TFrame")
employee_section.pack(pady=5)

label_employee = ttk.Label(employee_section, text="Select Employee", font=('Segoe UI', 14, 'bold'), style="TLabel")
label_employee.pack(anchor='center', pady=5)

employee_dict = fetch_employees()
employee_combo = ttk.Combobox(employee_section, values=list(employee_dict.keys()), state="readonly", width=35)
employee_combo.pack(pady=5)

# Button Frame
frame_buttons = ttk.Frame(root, padding=1, style="TFrame")
frame_buttons.pack(pady=1)

btn_time_in = ttk.Button(frame_buttons, text="Time In", command=time_in, width=20)
btn_time_in.grid(row=0, column=0, padx=10, pady=10)

btn_time_out = ttk.Button(frame_buttons, text="Time Out", command=time_out, width=20)
btn_time_out.grid(row=0, column=1, padx=10, pady=10)

btn_generate_reports = ttk.Button(frame_buttons, text="Generate Reports", command=generate_reports, width=43)
btn_generate_reports.grid(row=1, column=0, columnspan=2, pady=10)

btn_clear_attendance = ttk.Button(frame_buttons, text="Clear Attendance", command=clear_attendance, width=43)
btn_clear_attendance.grid(row=2, column=0, columnspan=2, pady=10)

# Rounded corners simulation (only partial support in ttk)
root.mainloop()