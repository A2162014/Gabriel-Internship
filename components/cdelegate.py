from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import QLineEdit, QStyledItemDelegate, QCompleter, QMessageBox

from maps import area_line_map_table


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter(parent)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        model = index.model()  # Get the model associated with the index

        completer_model = None  # Define completer_model with a default value of None

        # Set default suggestions for specific columns
        if index.column() in [2, 4]:  # Columns for AM/PM
            completer_model = QStringListModel(["AM", "PM"], parent=self.completer)
        elif index.column() == 6:  # Column for Area
            completer_model = QStringListModel(area_line_map_table.keys(), parent=self.completer)
        elif index.column() == 10:  # Column for Status
            completer_model = QStringListModel(["OK"], parent=self.completer)
        elif index.column() == 7:
            completer_model = self.get_line_suggestions(model, index, area_line_map_table)
        else:
            completer_model = self.get_unique_items(model, index)

        self.completer.setModel(completer_model)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        editor.setCompleter(self.completer)
        return editor

    def get_line_suggestions(self, model, index, categories):
        area_item = model.data(model.index(index.row(), 6))  # Get the area value from the model
        lines = categories.get(area_item, [])  # Get corresponding lines for the area from the categories mapping
        return QStringListModel(lines, parent=self.completer)

    def get_unique_items(self, model, index):
        items = set()  # Create a set to store unique items
        for row in range(model.rowCount()):
            item_text = model.data(model.index(row, index.column()))
            items.add(item_text)  # Add item to the set
        return QStringListModel(list(items), parent=self.completer)

    def setModelData(self, editor, model, index):
        entered_text = editor.text()
        completer_model = self.completer.model()
        column = index.column()

        # Check if the column is one of the exceptions
        if column not in [0, 1, 3, 5, 8, 9, 11]:
            if entered_text not in completer_model.stringList():
                # Show a warning or error message to the user
                QMessageBox.warning(editor, "Invalid Entry", "Please select a valid suggestion from the list.")
                return

        super().setModelData(editor, model, index)
