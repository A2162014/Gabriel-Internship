from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton

class WorkingDaysDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter Number of Working Days')
        self.layout = QVBoxLayout()
        self.label = QLabel("Enter the number of working days:")
        self.line_edit = QLineEdit()
        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.button_ok)
        self.setLayout(self.layout)

    def get_line_edit(self):
        return self.line_edit