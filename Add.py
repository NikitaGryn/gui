import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql.cursors
from view import StudentTable


class AddStudent(StudentTable):
    def __init__(self, student_table_instance, main_window, db_config_param):
        super().__init__(main_window, db_config_param)
        self.student_table = student_table_instance

    def add_student_to_db(self, student_data):
        connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                sql_insert_student = """
                INSERT INTO students (last_name, first_name, middle_name, group_name, 
                sem1_public_works, sem2_public_works, sem3_public_works, sem4_public_works, 
                sem5_public_works, sem6_public_works, sem7_public_works, sem8_public_works) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert_student, student_data)
                connection.commit()
                messagebox.showinfo("Успех", "Студент успешно добавлен в базу данных.")

        except pymysql.Error as e:
            print(f"Ошибка при добавлении студента в базу данных: {e}")
            messagebox.showerror("Ошибка", "Произошла ошибка при добавлении студента в базу данных.")

        finally:
            connection.close()

    def add_to_table(self, last_name_entry, first_name_entry, middle_name_entry, group_entry, semester_entries,
                     student_dialog):
        last_name = last_name_entry.get()
        first_name = first_name_entry.get()
        middle_name = middle_name_entry.get()
        group_name = group_entry.get()

        if not last_name or not first_name or not middle_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите Фамилию, Имя и Отчество.")
            return

        if not group_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите номер группы.")
            return

        try:
            group_number = int(group_name)
            if group_number <= 0:
                raise ValueError("Номер группы должен быть положительным числом.")
            if group_number > 10000:
                raise ValueError("Слишком большой номер группы.")

            for entry in semester_entries:
                semester_value = entry.get()
                if semester_value and (int(semester_value) < 0 or int(semester_value) > 100):
                    raise ValueError("Значение семестра должно быть в диапазоне от 0 до 100.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        semester_values_data = [entry.get() if entry.get() else "0" for entry in semester_entries]
        student_data = (last_name, first_name, middle_name, group_name, *semester_values_data)

        self.add_student_to_db(student_data)
        self.fetch_students_from_db()
        student_dialog.destroy()

    def add_student(self):
        student_dialog = tk.Toplevel(self.main_window)
        student_dialog.title("Добавление студента")
        student_dialog.geometry("320x450")

        ttk.Label(student_dialog, text="Фамилия:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(student_dialog, text="Имя:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(student_dialog, text="Отчество:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(student_dialog, text="Группа:").grid(row=3, column=0, padx=5, pady=5)

        last_name_entry = ttk.Entry(student_dialog)
        first_name_entry = ttk.Entry(student_dialog)
        middle_name_entry = ttk.Entry(student_dialog)
        group_entry = ttk.Entry(student_dialog)

        last_name_entry.grid(row=0, column=1, padx=5, pady=5)
        first_name_entry.grid(row=1, column=1, padx=5, pady=5)
        middle_name_entry.grid(row=2, column=1, padx=5, pady=5)
        group_entry.grid(row=3, column=1, padx=5, pady=5)

        semester_entries = []
        for i in range(1, 9):
            label = ttk.Label(student_dialog, text=f"{i} сем(общ. раб):")
            label.grid(row=i + 3, column=0, padx=5, pady=5)
            entry = ttk.Entry(student_dialog)
            entry.grid(row=i + 3, column=1, padx=5, pady=5)
            semester_entries.append(entry)

        add_button = ttk.Button(student_dialog, text="Добавить",
                                command=lambda: self.add_to_table(last_name_entry, first_name_entry, middle_name_entry,
                                                                  group_entry, semester_entries, student_dialog))
        add_button.grid(row=12, column=0, columnspan=2, pady=10)
