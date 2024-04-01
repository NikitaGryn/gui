import xml.sax


class StudentXMLHandler(xml.sax.ContentHandler):
    def __init__(self, student_table_instance):
        super().__init__()
        self.student_table = student_table_instance
        self.current_data = ""
        self.student_info = {}
        self.students_data = []

    def startElement(self, tag, attributes):
        self.current_data = tag
        if tag == "student":
            self.student_info = {}

    def characters(self, content):
        if self.current_data in self.student_info:
            self.student_info[self.current_data] += content
        else:
            self.student_info[self.current_data] = content

    def endElement(self, tag):
        if tag == "student":
            self.students_data.append((
                self.student_info.get("last_name", ""),
                self.student_info.get("first_name", ""),
                self.student_info.get("middle_name", ""),
                self.student_info.get("group_name", ""),
                self.student_info.get("sem1_public_works", ""),
                self.student_info.get("sem2_public_works", ""),
                self.student_info.get("sem3_public_works", ""),
                self.student_info.get("sem4_public_works", ""),
                self.student_info.get("sem5_public_works", ""),
                self.student_info.get("sem6_public_works", ""),
                self.student_info.get("sem7_public_works", ""),
                self.student_info.get("sem8_public_works", ""),
            ))

    def endDocument(self):
        for data in self.students_data:
            self.student_table.add_student_to_db(data)
