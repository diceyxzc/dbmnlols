import tkinter as tk
from tkinter import ttk, messagebox
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

        tree.column("Department", width=150)
        tree.column("Name", width=150)
        tree.column("Date", width=100)
        tree.column("Time In", width=100)
        tree.column("Time Out", width=100)

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
root.title("Employee Attendance System")
root.geometry("400x300")

# Styles
style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 12))
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TCombobox", font=("Segoe UI", 12))

# Top Frame
frame_top = ttk.Frame(root, padding=20)
frame_top.pack(fill=tk.X)

label_employee = ttk.Label(frame_top, text="Select Employee:")
label_employee.grid(row=0, column=0, padx=5, pady=5, sticky="w")

employee_dict = fetch_employees()
employee_combo = ttk.Combobox(frame_top, values=list(employee_dict.keys()), state="readonly", width=30)
employee_combo.grid(row=0, column=1, padx=5, pady=5)

# Button Frame

frame_buttons = ttk.Frame(root, padding=20)
frame_buttons.pack()

btn_clear_attendance = ttk.Button(frame_buttons, text="Clear Attendance", command=clear_attendance)
btn_clear_attendance.grid(row=2, column=0, columnspan=2, pady=10)

btn_time_in = ttk.Button(frame_buttons, text="Time In", command=time_in)
btn_time_in.grid(row=0, column=0, padx=10, pady=10)

btn_time_out = ttk.Button(frame_buttons, text="Time Out", command=time_out)
btn_time_out.grid(row=0, column=1, padx=10, pady=10)

btn_generate_reports = ttk.Button(frame_buttons, text="Generate Reports", command=generate_reports)
btn_generate_reports.grid(row=1, column=0, columnspan=2, pady=20)

# Start GUI
root.mainloop()