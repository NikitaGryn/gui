import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from search_student import Search
import pymysql


class Delete(Search):
    def __init__(self, main_window, db_config):
        super().__init__(main_window, db_config)

    def perform_deletion(self, delete_criteria, delete_value, min_public_works=None, max_public_works=None):
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()

            query = ""
            params = ()

            if delete_criteria == "По фамилии студента":
                query = "DELETE FROM students WHERE last_name = %s"
                params = (delete_value,)
            elif delete_criteria == "По номеру группы":
                query = "DELETE FROM students WHERE group_name = %s"
                params = (delete_value,)
            elif delete_criteria == "По фамилии студента и количеству общественной работы":
                if min_public_works is not None and max_public_works is not None:
                    query = ("DELETE FROM students WHERE last_name = %s AND %s <= (sem1_public_works + "
                             "sem2_public_works + sem3_public_works + sem4_public_works + sem5_public_works + "
                             "sem6_public_works + sem7_public_works + sem8_public_works) AND (sem1_public_works + "
                             "sem2_public_works + sem3_public_works + sem4_public_works + sem5_public_works + "
                             "sem6_public_works + sem7_public_works + sem8_public_works) <= %s")
                    params = (delete_value, min_public_works, max_public_works)
                else:
                    query = "DELETE FROM students WHERE last_name = %s"
                    params = (delete_value,)
            elif delete_criteria == "По номеру группы и количеству общественной работы":
                if min_public_works is not None and max_public_works is not None:
                    query = ("DELETE FROM students WHERE group_name = %s AND %s <= (sem1_public_works + "
                             "sem2_public_works + sem3_public_works + sem4_public_works + sem5_public_works + "
                             "sem6_public_works + sem7_public_works + sem8_public_works) AND (sem1_public_works + "
                             "sem2_public_works + sem3_public_works + sem4_public_works + sem5_public_works + "
                             "sem6_public_works + sem7_public_works + sem8_public_works) <= %s")
                    params = (delete_value, min_public_works, max_public_works)
                else:
                    query = "DELETE FROM students WHERE group_name = %s"
                    params = (delete_value,)

            if query:
                print("SQL-запрос:", cursor.mogrify(query, params))
                cursor.execute(query, params)
                conn.commit()

                deleted_count = cursor.rowcount
                conn.close()

                if deleted_count > 0:
                    messagebox.showinfo("Успех", f"Удаление завершено успешно. Удалено записей: {deleted_count}")
                else:
                    messagebox.showinfo("Успех", "Нет записей, удовлетворяющих условиям удаления.")

                self.fetch_students_from_db()
            else:
                messagebox.showwarning("Предупреждение", "Выбран некорректный критерий удаления.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при удалении студентов: {e}")

    def delete_students(self):
        delete_dialog = tk.Toplevel(self.main_window)
        delete_dialog.title("Удаление студентов")
        delete_dialog.geometry("400x200")

        ttk.Label(delete_dialog, text="Выберите критерии удаления:").pack(pady=5)

        delete_criteria = ttk.Combobox(delete_dialog, values=["По фамилии студента",
                                                              "По номеру группы",
                                                              "По фамилии студента и количеству общественной работы",
                                                              "По номеру группы и количеству общественной работы"],
                                       width=60)
        delete_criteria.pack(pady=5)
        delete_criteria.current(0)

        delete_value_label = ttk.Label(delete_dialog, text="Значение:")
        delete_value_entry = ttk.Entry(delete_dialog)

        def update_semester_entry_visibility():
            if delete_criteria.get() in ["По фамилии студента", "По номеру группы"]:
                min_public_works_label.pack_forget()
                min_public_works_entry.pack_forget()
                max_public_works_label.pack_forget()
                max_public_works_entry.pack_forget()
            else:
                min_public_works_label.pack()
                min_public_works_entry.pack()
                max_public_works_label.pack()
                max_public_works_entry.pack()

                if delete_criteria.get() in ["По фамилии студента и количеству общественной работы",
                                             "По номеру группы и количеству общественной работы"]:
                    min_public_works_label.pack()
                    min_public_works_entry.pack()
                    max_public_works_label.pack()
                    max_public_works_entry.pack()

        delete_criteria.bind("<<ComboboxSelected>>", lambda event: update_semester_entry_visibility())
        delete_value_label.pack(pady=5)
        delete_value_entry.pack(pady=5)

        min_public_works_label = ttk.Label(delete_dialog, text="Мин. общ. работы:")
        min_public_works_entry = ttk.Entry(delete_dialog)
        max_public_works_label = ttk.Label(delete_dialog, text="Макс. общ. работы:")
        max_public_works_entry = ttk.Entry(delete_dialog)

        update_semester_entry_visibility()

        min_public_works_entry.insert(0, "0")
        max_public_works_entry.insert(0, "100")

        delete_button = ttk.Button(delete_dialog, text="Удалить",
                                   command=lambda: self.perform_deletion(delete_criteria.get(),
                                                                         delete_value_entry.get(),
                                                                         min_public_works_entry.get() if
                                                                         min_public_works_entry.winfo_ismapped() else
                                                                         None,
                                                                         max_public_works_entry.get() if
                                                                         max_public_works_entry.winfo_ismapped() else
                                                                         None))
        delete_button.pack(pady=10)
