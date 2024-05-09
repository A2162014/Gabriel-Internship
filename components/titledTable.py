from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget


class TitledTableWidget(QWidget):
    def __init__(self, title, table_widget, parent=None):
        super().__init__(parent)
        self.table_widget = table_widget
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        title_label = QLabel(f"<h4>{title}</h4>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(self.table_widget)

    def setHorizontalHeaderLabels(self, labels):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.setHorizontalHeaderLabels(labels)
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def setEditTriggers(self, triggers):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.setEditTriggers(triggers)
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def setItem(self, row, column, item):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.setItem(row, column, item)
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def resizeRowsToContents(self):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.resizeRowsToContents()
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def resizeColumnsToContents(self):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.resizeColumnsToContents()
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def setSectionResizeMode(self, mode):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.horizontalHeader().setSectionResizeMode(mode)
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def setVerticalScrollBarPolicy(self, policy):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.setVerticalScrollBarPolicy(policy)
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def horizontalHeader(self):
        if isinstance(self.table_widget, QTableWidget):
            return self.table_widget.horizontalHeader()
        else:
            raise TypeError("Child widget is not a QTableWidget")

    def clearSelection(self):
        if isinstance(self.table_widget, QTableWidget):
            self.table_widget.clearSelection()
        else:
            raise TypeError("Child widget is not a QTableWidget")
