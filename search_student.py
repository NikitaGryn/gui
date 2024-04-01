import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
from pymysql import cursors


class Search:
    def __init__(self, main_window, db_config):
        self.main_window = main_window
        self.db_config = db_config
        self.result_tree = None

    def update_search_results(self, search_results):
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

        for student_row in search_results:
            student_values = [student_row['id'], student_row['last_name'], student_row['first_name'],
                              student_row['middle_name'], student_row['group_name'],
                              student_row['sem1_public_works'], student_row['sem2_public_works'],
                              student_row['sem3_public_works'], student_row['sem4_public_works'],
                              student_row['sem5_public_works'], student_row['sem6_public_works'],
                              student_row['sem7_public_works'], student_row['sem8_public_works']]
            self.result_tree.insert("", tk.END, values=student_values)

    def perform_search(self, search_criteria, search_value, min_semester_value, max_semester_value):
        try:
            min_semester_value = int(min_semester_value) if min_semester_value.isdigit() else 0
            max_semester_value = int(max_semester_value) if max_semester_value.isdigit() else 100

            if min_semester_value > max_semester_value:
                messagebox.showerror("Ошибка", "Минимальный предел семестра должен быть меньше или равен максимальному")
                return

            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            query = ""
            if search_criteria == "По фамилии":
                query = "SELECT * FROM students WHERE last_name = %s"
            elif search_criteria == "По номеру группы":
                query = "SELECT * FROM students WHERE group_name = %s"
            elif search_criteria == "По фамилии студента и количеству общественной работы":
                query = "SELECT * FROM students WHERE last_name = %s"
            elif search_criteria == "По номеру группы и количеству общественной работы":
                query = "SELECT * FROM students WHERE group_name = %s"

            query += " AND ("
            for i in range(1, 9):
                query += f"{min_semester_value} <= sem{i}_public_works AND sem{i}_public_works <= {max_semester_value} "
                if i != 8:
                    query += "AND "
            query += ")"

            cursor.execute(query, (search_value,))

            print("SQL-запрос:", cursor.mogrify(query, (search_value,)))

            search_results = cursor.fetchall()
            print("Результаты запроса:", search_results)

            conn.close()

            self.display_search_results(search_results)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выполнении поиска: {e}")

    def display_search_results(self, search_results):
        result_window = tk.Toplevel(self.main_window)
        result_window.title("Результаты поиска")

        result_frame = ttk.Frame(result_window)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_tree = ttk.Treeview(result_frame, columns=(
            "ID", "Фамилия", "Имя", "Отчество", "Группа", "1 сем(общ. раб)", "2 сем(общ. раб)", "3 сем(общ. раб)",
            "4 сем(общ. раб)", "5 сем(общ. раб)", "6 сем(общ. раб)", "7 сем(общ. раб)", "8 сем(общ. раб)"),
                                        show="headings")
        self.result_tree.heading("ID", text="ID")
        self.result_tree.heading("Фамилия", text="Фамилия")
        self.result_tree.heading("Имя", text="Имя")
        self.result_tree.heading("Отчество", text="Отчество")
        self.result_tree.heading("Группа", text="Группа")
        for i in range(1, 9):
            self.result_tree.heading(f"{i} сем(общ. раб)", text=f"{i} сем(общ. раб)")

        self.update_search_results(search_results)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    def get_group_list(self):
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT group_name FROM students")
            groups = [row[0] for row in cursor.fetchall()]
            conn.close()
            return groups
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при получении списка групп: {e}")
            return []

    def search_students(self):
        search_dialog = tk.Toplevel(self.main_window)
        search_dialog.title("Поиск студента")
        search_dialog.geometry("500x300")
        ttk.Label(search_dialog, text="Выберите критерии поиска:").grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        search_criteria = ttk.Combobox(search_dialog, values=["По фамилии",
                                                              "По номеру группы",
                                                              "По фамилии студента и количеству общественной работы",
                                                              "По номеру группы и количеству общественной работы"],
                                       width=60)  # Установка ширины Combobox
        search_criteria.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        search_criteria.current(0)

        last_name_label = ttk.Label(search_dialog, text="Фамилия:")
        last_name_entry = ttk.Entry(search_dialog)
        group_label = ttk.Label(search_dialog, text="Номер группы:")
        group_combobox = ttk.Combobox(search_dialog, values=self.get_group_list(), width=60)
        min_semester_label = ttk.Label(search_dialog, text="Минимальный семестр:")
        min_semester_entry = ttk.Entry(search_dialog)
        max_semester_label = ttk.Label(search_dialog, text="Максимальный семестр:")
        max_semester_entry = ttk.Entry(search_dialog)

        ttk.Button(search_dialog, text="Искать",
                   command=lambda: self.perform_search(search_criteria.get(),
                                                       search_value=last_name_entry.get() if search_criteria.get() in [
                                                           "По фамилии",
                                                           "По фамилии студента и количеству общественной работы"] else
                                                       group_combobox.get(),
                                                       min_semester_value=min_semester_entry.get(),
                                                       max_semester_value=max_semester_entry.get())).grid(row=6,
                                                                                                          column=0,
                                                                                                          columnspan=2,
                                                                                                          pady=10)

        def update_search_fields():
            search_criteria_value = search_criteria.get()
            if search_criteria_value in ["По фамилии", "По фамилии студента и количеству общественной работы"]:
                last_name_label.grid(row=2, column=0, padx=5, pady=5)
                last_name_entry.grid(row=2, column=1, padx=5, pady=5)
            else:
                last_name_label.grid_forget()
                last_name_entry.grid_forget()

            if search_criteria_value in ["По номеру группы", "По номеру группы и количеству общественной работы"]:
                group_label.grid(row=3, column=0, padx=5, pady=5)
                group_combobox.grid(row=3, column=1, padx=5, pady=5)
            else:
                group_label.grid_forget()
                group_combobox.grid_forget()

            if search_criteria_value in ["По фамилии студента и количеству общественной работы",
                                         "По номеру группы и количеству общественной работы"]:
                min_semester_label.grid(row=4, column=0, padx=5, pady=5)
                min_semester_entry.grid(row=4, column=1, padx=5, pady=5)
                max_semester_label.grid(row=5, column=0, padx=5, pady=5)
                max_semester_entry.grid(row=5, column=1, padx=5, pady=5)
            else:
                min_semester_label.grid_forget()
                min_semester_entry.grid_forget()
                max_semester_label.grid_forget()
                max_semester_entry.grid_forget()

        update_search_fields()
        search_criteria.bind("<<ComboboxSelected>>",
                             lambda event: update_search_fields())
