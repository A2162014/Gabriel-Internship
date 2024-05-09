from PyQt5.QtWidgets import QLineEdit


class HoverPlaceholderLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder_text = ""
        self.setPlaceholderText("")

    def setHoverPlaceholderText(self, text):
        self.placeholder_text = text

    def enterEvent(self, event):
        self.setPlaceholderText(self.placeholder_text)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setPlaceholderText("")
        super().leaveEvent(event)
