from PyQt5.QtWidgets import QLabel, QDialog, QLineEdit, QMessageBox, QPushButton, QVBoxLayout


class StatisticsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter Values for Statistics')
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        questions = [
            "Number of working days:",
            "Target in % for each Location:",
            "Target in Day's for each location:",
            "Target in Min's for each location:",
            "Target in % for each line in SX Damper & FA:",
            "Target in % for each line in Front Fork Final Assembly:",
            "Target in % OT Cell & IT Grinding:"
        ]
        self.line_edits = []
        for question in questions:
            label = QLabel(question)
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)
            layout.addWidget(label)
            layout.addWidget(line_edit)
        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_values)
        layout.addWidget(button_ok)
        self.setLayout(layout)

    def check_values(self):
        values = [line_edit.text() for line_edit in self.line_edits]
        if not all(values):
            self.show_missing_value_warning()
            return
        for value, line_edit in zip(values, self.line_edits):
            if not (value.strip().isdigit() or self.is_float(value.strip())):
                self.show_invalid_input_warning()
                line_edit.clear()
                return
        self.accept()

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def show_invalid_input_warning(self):
        QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value.")

    def show_missing_value_warning(self):
        QMessageBox.warning(self, "Missing Value", "Please enter all the required values.")

    def get_line_edits(self):
        return [line_edit.text() for line_edit in self.line_edits]
