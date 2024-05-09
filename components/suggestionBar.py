from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QCompleter, QLineEdit, QMessageBox, QStyledItemDelegate
from maps import (connect_to_database, fetch_values, fetch_area_line_data, create_area_line_map,
                  fetch_line_machine_data, create_line_machine_map, fetch_machine_problem_data,
                  create_machine_problem_map, fetch_problem_caction_data, create_problem_caction_map)


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter(parent)

        with connect_to_database() as conn:
            self.anames_list = fetch_values(conn, "SELECT ANAME FROM AREA")
            area_line_data = fetch_area_line_data(conn)
            self.area_line_map = create_area_line_map(area_line_data)
            line_machine_data = fetch_line_machine_data(conn)
            self.line_machine_map = create_line_machine_map(line_machine_data)
            machine_problem_data = fetch_machine_problem_data(conn)
            self.machine_problem_map = create_machine_problem_map(machine_problem_data)
            problem_caction_data = fetch_problem_caction_data(conn)
            self.problem_caction_map = create_problem_caction_map(problem_caction_data)
            conn.commit()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        model = index.model()
        completer_model = None
        column = index.column()
        if column in [2, 4]:
            completer_model = QStringListModel(["AM", "PM"], parent=self.completer)
        elif column == 6:
            completer_model = QStringListModel(self.anames_list, parent=self.completer)
        elif column == 7:
            completer_model = self.get_line_suggestions(model, index)
        elif column == 8:
            completer_model = self.get_machine_suggestions(model, index)
        elif column == 9:
            completer_model = self.get_problem_suggestions(model, index)
        elif column == 10:
            completer_model = QStringListModel(["OK"], parent=self.completer)
        elif column == 12:
            completer_model = self.get_corrective_action_suggestions(model, index)
        else:
            completer_model = self.get_unique_items(model, index)
        self.completer.setModel(completer_model)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        editor.setCompleter(self.completer)
        return editor

    def get_line_suggestions(self, model, index):
        area_item = model.data(model.index(index.row(), 6))
        lines = self.area_line_map.get(area_item, [])
        return QStringListModel(lines, parent=self.completer)

    def get_machine_suggestions(self, model, index):
        line_item = model.data(model.index(index.row(), 7))
        machines = self.line_machine_map.get(line_item, [])
        return QStringListModel(machines, parent=self.completer)

    def get_problem_suggestions(self, model, index):
        machine_item = model.data(model.index(index.row(), 8))
        problems = self.machine_problem_map.get(machine_item, [])
        return QStringListModel(problems, parent=self.completer)

    def get_corrective_action_suggestions(self, model, index):
        problem_item = model.data(model.index(index.row(), 9))
        actions = self.problem_caction_map.get(problem_item, [])
        return QStringListModel(actions, parent=self.completer)

    def get_unique_items(self, model, index):
        items = {model.data(model.index(row, index.column())) for row in range(model.rowCount())}
        return QStringListModel(list(items), parent=self.completer)

    def setModelData(self, editor, model, index):
        entered_text = editor.text()
        completer_model = self.completer.model()
        column = index.column()
        if column not in [0, 1, 3, 5, 8, 9, 11] and entered_text not in completer_model.stringList():
            QMessageBox.warning(editor, "Invalid Entry", "Please select a valid suggestion from the list.")
            return

        super().setModelData(editor, model, index)
