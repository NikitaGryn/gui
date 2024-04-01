import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from search_student import Search
from delete_student import Delete
import pymysql.cursors
import xml.sax
from lol import StudentXMLHandler


class StudentTable(Delete, Search):
    def __init__(self, main_window, db_config_param):
        super().__init__(main_window, db_config_param)

        self.main_window = main_window
        self.student_id = 1
        self.table = None
        self.table_data = []
        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.setup_window()
        self.main_frame = ttk.Frame(self.main_window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.button_frame = None
        self.first_page_button = None
        self.prev_page_button = None
        self.next_page_button = None
        self.last_page_button = None
        self.delete_button = None
        self.search_button = None
        self.add_button = None
        self.file_button = None
        self.page_info_label = None
        self.page_size_label = None
        self.page_size_entry = None
        self.page_size_button = None
        self.show_tree_button = None

        self.host = db_config_param['host']
        self.user = db_config_param['user']
        self.password = db_config_param['password']
        self.database = db_config_param['database']

        self.setup_buttons()

        self.setup_table()

        self.fetch_students_from_db()

        self.update_main_table()

        self.setup_page_buttons()

    def setup_page_buttons(self):
        self.page_info_label = ttk.Label(self.main_frame, text="")
        self.page_info_label.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.page_size_label = ttk.Label(self.main_frame, text="Записей на странице:")
        self.page_size_label.pack(side=tk.BOTTOM, padx=10, pady=5)

        self.page_size_entry = ttk.Entry(self.main_frame)
        self.page_size_entry.insert(0, str(self.page_size))
        self.page_size_entry.pack(side=tk.BOTTOM, padx=10, pady=5)

        self.page_size_button = ttk.Button(self.main_frame, text="Изменить", command=self.change_page_size)
        self.page_size_button.pack(side=tk.BOTTOM, padx=10, pady=5)

        self.update_page_info()

        self.show_tree_button = ttk.Button(self.button_frame, text="Показать в виде дерева",
                                           command=self.show_tree_view)
        self.show_tree_button.grid(row=0, column=8, padx=5, pady=5)

    def setup_window(self):
        self.main_window.resizable(False, False)
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()

        window_width = 2000
        window_height = 300
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.main_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def setup_table(self):
        self.main_frame = ttk.Frame(self.main_window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем таблицу
        self.table = ttk.Treeview(self.main_frame, columns=(
            "ID", "Фамилия", "Имя", "Отчество",
            "Группа", "1 сем(общ. раб)", "2 сем(общ. раб)", "3 сем(общ. раб)", "4 сем(общ. раб)",
            "5 сем(общ. раб)", "6 сем(общ. раб)", "7 сем(общ. раб)", "8 сем(общ. раб)"), show="headings")
        self.table.heading("ID", text="ID")
        self.table.heading("Фамилия", text="Фамилия")
        self.table.heading("Имя", text="Имя")
        self.table.heading("Отчество", text="Отчество")
        self.table.heading("Группа", text="Группа")
        for i in range(1, 9):
            self.table.heading(f"{i} сем(общ. раб)", text=f"{i} сем(общ. раб)")

        self.table.column("ID", width=50, anchor=tk.CENTER)
        self.table.column("Фамилия", width=100, anchor=tk.CENTER)
        self.table.column("Имя", width=100, anchor=tk.CENTER)
        self.table.column("Отчество", width=100, anchor=tk.CENTER)
        self.table.column("Группа", width=100, anchor=tk.CENTER)
        for i in range(1, 9):
            self.table.column(f"{i} сем(общ. раб)", width=100, anchor=tk.CENTER)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.first_page_button = ttk.Button(self.button_frame, text="Первая", command=self.go_to_first_page)
        self.first_page_button.grid(row=0, column=0, padx=5, pady=5)

        self.prev_page_button = ttk.Button(self.button_frame, text="Предыдущая", command=self.go_to_previous_page)
        self.prev_page_button.grid(row=0, column=1, padx=5, pady=5)

        self.next_page_button = ttk.Button(self.button_frame, text="Следующая", command=self.go_to_next_page)
        self.next_page_button.grid(row=0, column=2, padx=5, pady=5)

        self.last_page_button = ttk.Button(self.button_frame, text="Последняя", command=self.go_to_last_page)
        self.last_page_button.grid(row=0, column=3, padx=5, pady=5)

        self.delete_button = ttk.Button(self.button_frame, text="Удалить", command=self.delete_students)
        self.delete_button.grid(row=0, column=4, padx=5, pady=5)

        self.search_button = ttk.Button(self.button_frame, text="Поиск", command=self.search_students)
        self.search_button.grid(row=0, column=5, padx=5, pady=5)

        self.add_button = ttk.Button(self.button_frame, text="Добавить студента", command=self.add_student)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)

        self.file_button = ttk.Button(self.button_frame, text="Считать с файла xml", command=self.load_data_from_xml)
        self.file_button.grid(row=0, column=7, padx=5, pady=5)

        self.file_button = ttk.Button(self.button_frame, text="Загрузить в файл xml", command=self.save_student_to_xml)
        self.file_button.grid(row=0, column=9, padx=5, pady=5)

    def show_tree_view(self):
        tree_view_dialog = tk.Toplevel(self.main_window)
        tree_view_dialog.title("Дерево записей")
        tree_view_dialog.geometry("800x600")

        tree = ttk.Treeview(tree_view_dialog)
        tree.pack(fill=tk.BOTH, expand=True)

        root_node = tree.insert("", tk.END, text="Студенты")

        for student_row in self.table_data:
            student_info = (f"{student_row['last_name']} {student_row['first_name']} {student_row['middle_name']} - "
                            f"{student_row['group_name']}")
            student_node = tree.insert(root_node, tk.END, text=student_info)
            tree.insert(student_node, tk.END, text=f"1 сем(общ. раб): {student_row['sem1_public_works']}")
            tree.insert(student_node, tk.END, text=f"2 сем(общ. раб): {student_row['sem2_public_works']}")
            tree.insert(student_node, tk.END, text=f"3 сем(общ. раб): {student_row['sem3_public_works']}")
            tree.insert(student_node, tk.END, text=f"4 сем(общ. раб): {student_row['sem4_public_works']}")
            tree.insert(student_node, tk.END, text=f"5 сем(общ. раб): {student_row['sem5_public_works']}")
            tree.insert(student_node, tk.END, text=f"6 сем(общ. раб): {student_row['sem6_public_works']}")
            tree.insert(student_node, tk.END, text=f"7 сем(общ. раб): {student_row['sem7_public_works']}")
            tree.insert(student_node, tk.END, text=f"8 сем(общ. раб): {student_row['sem8_public_works']}")

        tree_view_dialog.mainloop()

    def load_data_from_xml(self):
        filename = filedialog.askopenfilename(title="Выберите XML файл", filetypes=(("XML files", "*.xml"),))
        if filename:
            try:
                xml_handler = StudentXMLHandler(self)
                parser = xml.sax.make_parser()
                parser.setContentHandler(xml_handler)
                parser.parse(filename)

                self.fetch_students_from_db()

                messagebox.showinfo("Успех", "Данные успешно загружены из файла.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {e}")

    def save_student_to_xml(self):
        try:
            selected_item = self.table.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите студента.")
                return

            student_id = self.table.item(selected_item)['values'][0]

            filename = filedialog.asksaveasfilename(
                title="Сохранить данные студента как XML",
                defaultextension=".xml",
                filetypes=(("XML files", "*.xml"),)
            )

            if filename:
                with open(filename, 'w') as file:
                    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    file.write('<students>\n')
                    host = 'localhost'
                    user = 'lupach'
                    password = '228'
                    database = 'kek'
                    connection = pymysql.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database,
                        cursorclass=pymysql.cursors.DictCursor
                    )

                    try:
                        with connection.cursor() as cursor:
                            sql_select_student = "SELECT * FROM students WHERE id = %s"
                            cursor.execute(sql_select_student, student_id)
                            student_data = cursor.fetchone()

                            if student_data:
                                file.write('\t<student>\n')
                                for key, value in student_data.items():
                                    file.write(f'\t\t<{key}>{value}</{key}>\n')
                                file.write('\t</student>\n')
                    except pymysql.Error as e:
                        print(f"Ошибка при получении данных студента из базы данных: {e}")
                    finally:
                        connection.close()

                    file.write('</students>\n')
                    messagebox.showinfo("Успех", "Данные студента успешно сохранены в XML файл.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения данных студента в XML файл: {e}")

    def update_page_info(self):
        total_records = len(self.table_data)
        start_index = (self.current_page - 1) * self.page_size + 1
        end_index = min(start_index + self.page_size - 1, total_records)
        self.page_info_label.config(
            text=f"Страница {self.current_page}/{self.total_pages}, " +
                 f"Отображается {start_index}-{end_index} из {total_records} записей")

    def change_page_size(self):
        try:
            new_page_size = int(self.page_size_entry.get())
            if new_page_size <= 0:
                messagebox.showerror("Ошибка", "Число записей на странице должно быть положительным.")
                return
            self.page_size = new_page_size
            self.update_table_with_pagination()
            self.update_page_info()
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число записей на странице.")

    def update_table_with_pagination(self):
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, len(self.table_data))

        for row in self.table.get_children():
            self.table.delete(row)

        for student_row in self.table_data[start_index:end_index]:
            student_values = [student_row['id'], student_row['last_name'], student_row['first_name'],
                              student_row['middle_name'], student_row['group_name'],
                              student_row['sem1_public_works'], student_row['sem2_public_works'],
                              student_row['sem3_public_works'], student_row['sem4_public_works'],
                              student_row['sem5_public_works'], student_row['sem6_public_works'],
                              student_row['sem7_public_works'], student_row['sem8_public_works']]
            self.table.insert("", tk.END, values=student_values)

        self.total_pages = (len(self.table_data) + self.page_size - 1) // self.page_size

        self.update_page_control_buttons()

        self.update_page_info()

    def update_page_control_buttons(self):
        self.total_pages = (len(self.table_data) + self.page_size - 1) // self.page_size

        self.first_page_button.config(state="normal" if self.current_page > 1 else "disabled")
        self.prev_page_button.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_page_button.config(state="normal" if self.current_page < self.total_pages else "disabled")
        self.last_page_button.config(state="normal" if self.current_page < self.total_pages else "disabled")

    def go_to_first_page(self):
        self.current_page = 1
        self.update_table_with_pagination()

    def go_to_previous_page(self):
        self.current_page -= 1
        self.update_table_with_pagination()

    def go_to_next_page(self):
        self.current_page += 1
        self.update_table_with_pagination()

    def go_to_last_page(self):
        self.current_page = self.total_pages
        self.update_table_with_pagination()

    def fetch_students_from_db(self):
        connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                sql_select_students = """
                SELECT * FROM students
                """
                cursor.execute(sql_select_students)
                self.table_data = cursor.fetchall()
                self.update_main_table()

        except pymysql.Error as e:
            print(f"Ошибка при получении списка студентов из базы данных: {e}")

        finally:
            connection.close()

    def update_main_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for student_row in self.table_data:
            student_values = [student_row['id'], student_row['last_name'], student_row['first_name'],
                              student_row['middle_name'], student_row['group_name'],
                              student_row['sem1_public_works'], student_row['sem2_public_works'],
                              student_row['sem3_public_works'], student_row['sem4_public_works'],
                              student_row['sem5_public_works'], student_row['sem6_public_works'],
                              student_row['sem7_public_works'], student_row['sem8_public_works']]
            self.table.insert("", tk.END, values=student_values)
