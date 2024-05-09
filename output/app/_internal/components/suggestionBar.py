from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import (
    QCompleter, QLineEdit, QMessageBox, QStyledItemDelegate
)

from helpers.maps import connect_to_database, create_full_map, extract_full_mappings


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter(parent)

        with connect_to_database() as conn:
            self.single_map = create_full_map(conn)
            self.area_line_map, self.line_machine_map, self.machine_problem_map, self.problem_caction_map = extract_full_mappings(
                self.single_map)

            conn.commit()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        model = index.model()
        completer_model = None
        column = index.column()
        if column in [3, 5]:
            completer_model = QStringListModel(["AM", "PM"], parent=self.completer)
        elif column == 7:
            completer_model = QStringListModel(list(self.area_line_map.keys()), parent=self.completer)
        elif column == 8:
            selected_area_index = model.index(index.row(), 7)
            selected_area = model.data(selected_area_index)
            if selected_area in self.area_line_map:
                completer_model = QStringListModel(self.area_line_map[selected_area], parent=self.completer)
            else:
                completer_model = QStringListModel([], parent=self.completer)
        elif column == 9:
            selected_line_index = model.index(index.row(), 8)
            selected_line = model.data(selected_line_index)
            if selected_line in self.line_machine_map:
                completer_model = QStringListModel(self.line_machine_map[selected_line], parent=self.completer)
            else:
                completer_model = QStringListModel([], parent=self.completer)
        elif column == 10:
            selected_machine_index = model.index(index.row(), 9)
            selected_machine = model.data(selected_machine_index)
            if selected_machine in self.machine_problem_map:
                completer_model = QStringListModel(self.machine_problem_map[selected_machine],
                                                   parent=self.completer)
            else:
                completer_model = QStringListModel([],
                                                   parent=self.completer)
        elif column == 11:
            completer_model = QStringListModel(["OK"], parent=self.completer)
        elif column == 13:
            selected_problem_index = model.index(index.row(), 10)
            selected_problem = model.data(selected_problem_index)
            if selected_problem in self.problem_caction_map:
                completer_model = QStringListModel(self.problem_caction_map[selected_problem],
                                                   parent=self.completer)
            else:
                completer_model = QStringListModel([],
                                                   parent=self.completer)
        else:
            completer_model = self.get_unique_items(model, index)
        if completer_model:
            self.completer.setModel(completer_model)
            self.completer.setCompletionMode(QCompleter.PopupCompletion)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            editor.setCompleter(self.completer)
        return editor

    def get_unique_items(self, model, index):
        items = {model.data(model.index(row, index.column())) for row in range(model.rowCount())}
        return QStringListModel(list(items), parent=self.completer)

    def setModelData(self, editor, model, index):
        entered_text = editor.text()
        completer_model = self.completer.model()
        column = index.column()
        if column not in [0, 1, 2, 4, 6, 9, 10, 12] and entered_text not in completer_model.stringList():
            QMessageBox.warning(editor, "Invalid Entry", "Please select a valid suggestion from the list.")
            return

        super().setModelData(editor, model, index)
