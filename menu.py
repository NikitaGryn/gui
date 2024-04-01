import tkinter as tk
from tkinter import ttk
from Add import AddStudent

if __name__ == "__main__":
    root = tk.Tk()
    my_table = ttk.Treeview(root)
    my_table_data = []
    db_config = {'host': 'localhost', 'user': 'lupach', 'password': '228', 'database': 'kek'}

    add_student_instance = AddStudent(my_table, root, db_config)
    add_student_instance.fetch_students_from_db()

    root.mainloop()
