from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout


class CustomWidget(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.button = QPushButton(name)
        self.button.setMinimumSize(200, 50)  # Set minimum size to prevent vertical shrinking
        self.button.setMaximumSize(200, 50)  # Set minimum size to prevent vertical shrinking

        # Set the tooltip to display the same name when hovering over the button.
        self.button.setToolTip(name)

        layout = QHBoxLayout()
        layout.addWidget(self.button)
        layout.setAlignment(Qt.AlignLeft)  # Set alignment of the layout to left

        self.setLayout(layout)

        # Apply styles to the custom widget
        self.setStyleSheet('''
            font-size: 16px;
            text-align: left;
        ''')

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())
