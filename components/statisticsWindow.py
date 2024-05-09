from PyQt5.QtWidgets import (
    QLabel, QDialog, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QWidget, QHBoxLayout,
    QFrame
)


class StatisticsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter Values for Statistics')
        self.setMinimumSize(825, 425)
        self.setup_ui()

    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        grid_layout = QGridLayout()
        questions = [
            "Number of working days in January:",
            "Number of working days in February:",
            "Number of working days in March:",
            "Number of working days in April:",
            "Number of working days in May:",
            "Number of working days in June:",
            "Number of working days in July:",
            "Number of working days in August:",
            "Number of working days in September:",
            "Number of working days in October:",
            "Number of working days in November:",
            "Number of working days in December:",
            "Target in % for each Location:",
            "Target in Day's for each location:",
            "Target in Min's for each location:",
            "Target in % for each line in SX Damper & FA:",
            "Target in % for each line in Front Fork Final Assembly:",
            "Target in % for each line in OT Cell & IT Grinding:",
            "Target in % for each machine in SX Damper & FA:",
            "Target in % for each machine in Front Fork Final Assembly:",
            "Target in % for each machine in OT Cell & IT Grinding:"
        ]
        self.line_edits = []
        half_len = len(questions) // 2
        for i, question in enumerate(questions[:half_len]):
            label = QLabel(question)
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(line_edit, i, 1)
        for i, question in enumerate(questions[half_len:], start=half_len):
            label = QLabel(question)
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)
            grid_layout.addWidget(label, i - half_len, 2)
            grid_layout.addWidget(line_edit, i - half_len, 3)
        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_values)
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(button_ok)
        layout.addLayout(grid_layout)
        layout.addLayout(horizontal_layout)
        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def check_values(self):
        for line_edit in self.line_edits:
            value = line_edit.text().strip()
            if value == '':
                self.show_missing_value_warning()
                return
            if not (value.isdigit() or self.is_float(value)):
                self.show_invalid_input_warning()
                line_edit.clear()
                return
        self.accept()

    @staticmethod
    def is_float(value):
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
