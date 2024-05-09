import os
import sys

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QKeySequence, QRegExpValidator, QIntValidator, QIcon
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton,
                             QScrollArea, QSplitter, QShortcut, QTableWidget, QTreeWidget, QTabWidget, QVBoxLayout,
                             QWidget, QAbstractItemView, QTreeWidgetItem, QAction, QMenuBar)

from components.hoverPlaceholder import HoverPlaceholderLineEdit
from components.suggestionBar import CompleterDelegate
from helpers.maps import column_headers, month_map, stat_headers, current_dir
from helpers.tab1Utils import (edit_cell, new_table, open_table, save_table,
                               validate_and_check_item, tab_changed, ask_statistic_values)
from helpers.tab2Utils import (add_data_to_database, remove_data_from_database,
                               update_tree_widget)
from helpers.tab3Tools import save_statistics, display_statistics
from materials.styles import bodyStyle, scrollStyle, statisticsStyle, tableStyle, treeStyle, menuSyle


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Breakdown Register – Gabriel India Limited')
        im_path = os.path.join(os.path.dirname(current_dir), 'materials\\app_icon.png')
        self.setWindowIcon(QIcon(im_path))
        self.setMinimumSize(1280, 720)
        self.initUI()

    def initUI(self):
        new_table_action = QAction('&New Table', self)
        new_table_action.setShortcut('Ctrl+N')
        new_table_action.triggered.connect(lambda: new_table(self.right_line_edit, self.table_widget, self.tab_widget))
        open_table_action = QAction('&Open Table', self)
        open_table_action.setShortcut('Ctrl+O')
        open_table_action.triggered.connect(
            lambda: open_table(self.right_line_edit, self.table_widget, self.tab_widget))
        save_table_action = QAction('&Save Table', self)
        save_table_action.setShortcut('Ctrl+S')
        save_table_action.triggered.connect(lambda: save_table(self.table_widget))
        edit_stat_values_action = QAction('&Edit Statistic Values', self)
        edit_stat_values_action.setShortcut('Ctrl+E')
        edit_stat_values_action.triggered.connect(
            lambda: ask_statistic_values(self.tree_widget_left))
        save_statistics_action = QAction('&Save Statistics', self)
        save_statistics_action.setShortcut(QKeySequence("Ctrl+S"))
        save_statistics_action.triggered.connect(lambda: save_statistics(self.tab3_scroll_area))
        menubar = QMenuBar()
        menubar.setStyleSheet(menuSyle)
        table_menu = menubar.addMenu('&Table')
        table_menu.addAction(new_table_action)
        table_menu.addAction(open_table_action)
        table_menu.addAction(save_table_action)
        statistics_menu = menubar.addMenu('&Statistics')
        statistics_menu.addAction(edit_stat_values_action)
        statistics_menu.addAction(save_statistics_action)
        table_menu.setEnabled(True)
        for action in table_menu.actions():
            action.setEnabled(True)
        statistics_menu.setEnabled(False)
        for action in statistics_menu.actions():
            action.setEnabled(False)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(menubar)
        self.tab_widget = QTabWidget()
        self.data_entry_tab = QWidget()
        self.data_entry_layout = QVBoxLayout(self.data_entry_tab)
        self.splitter = QSplitter(Qt.Horizontal)
        self.right_layout = QVBoxLayout()
        self.right_line_edit = QLineEdit()
        self.right_line_edit.setReadOnly(True)
        self.right_layout.addWidget(self.right_line_edit)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(column_headers))
        self.table_widget.setHorizontalHeaderLabels(column_headers)
        self.table_widget.setStyleSheet(tableStyle)
        self.right_layout.addWidget(self.table_widget)
        self.table_widget.setColumnWidth(12, 200)
        self.table_widget.horizontalHeader().setSectionResizeMode(12, QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(12, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 12)
            if item:
                item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        self.table_widget.resizeRowsToContents()
        self.right_line_edit.hide()
        copy_shortcut = QShortcut(QKeySequence.Copy, self)
        copy_shortcut.activated.connect(self.copy_cells)
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setStretchFactor(1, 7)
        self.data_entry_layout.addWidget(self.splitter)
        self.data_entry_tab.setLayout(self.data_entry_layout)
        self.tab_widget.addTab(self.data_entry_tab, "Edit Table")
        self.tab2_widget = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2_horizontal_layout = QHBoxLayout()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet(treeStyle)
        self.scroll_area_tab2 = QScrollArea()
        self.scroll_area_tab2.setStyleSheet(scrollStyle)
        self.scroll_area_tab2.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        area_layout = QHBoxLayout()
        line_layout = QHBoxLayout()
        time_layout = QHBoxLayout()
        machine_layout = QHBoxLayout()
        problem_layout = QHBoxLayout()
        corrective_action_layout = QHBoxLayout()
        capital_pattern = QRegExp("[A-Z0-9][A-Z0-9\s\-/]*")
        capital_validator = QRegExpValidator(capital_pattern)
        line_full_pattern = QRegExp("[A-Z][a-zA-Z0-9\s\-/]*")
        line_full_validator = QRegExpValidator(line_full_pattern)
        whole_number_validator = QIntValidator()
        whole_number_validator.setBottom(0)
        self.area_label = QLabel("Area:")
        self.area_value_line_edit_short = HoverPlaceholderLineEdit()
        self.area_value_line_edit_short.setReadOnly(True)
        self.area_value_line_edit_short.setHoverPlaceholderText("Tabular Name – CAPITAL letters only")
        self.area_value_line_edit_full = HoverPlaceholderLineEdit()
        self.area_value_line_edit_full.setReadOnly(True)
        self.area_value_line_edit_full.setHoverPlaceholderText("Statistical Name")
        self.line_label = QLabel("Line:")
        self.line_value_line_edit_short = HoverPlaceholderLineEdit()
        self.line_value_line_edit_short.setValidator(capital_validator)
        self.line_value_line_edit_short.setHoverPlaceholderText("Tabular Name – CAPITAL letters only")
        self.line_value_line_edit_full = HoverPlaceholderLineEdit()
        self.line_value_line_edit_full.setValidator(line_full_validator)
        self.line_value_line_edit_full.setHoverPlaceholderText("Statistical Name")
        self.time_label = QLabel("Time Availability:")
        self.time_value_line_edit = HoverPlaceholderLineEdit()
        self.time_value_line_edit.setValidator(whole_number_validator)
        self.time_value_line_edit.setHoverPlaceholderText("Whole numbers only")
        self.machine_label = QLabel("Machine:")
        self.machine_line_edit = HoverPlaceholderLineEdit()
        self.machine_line_edit.setValidator(capital_validator)
        self.machine_line_edit.setHoverPlaceholderText("CAPITAL letters only")
        self.problem_label = QLabel("Problem:")
        self.problem_line_edit = HoverPlaceholderLineEdit()
        self.problem_line_edit.setValidator(capital_validator)
        self.problem_line_edit.setHoverPlaceholderText("CAPITAL letters only")
        self.corrective_action_label = QLabel("Corrective Action:")
        self.corrective_action_line_edit = HoverPlaceholderLineEdit()
        self.corrective_action_line_edit.setValidator(capital_validator)
        self.corrective_action_line_edit.setHoverPlaceholderText("CAPITAL letters only")
        self.machine_line_edit.textChanged.connect(self.updateLineEditsReadOnly)
        self.problem_line_edit.textChanged.connect(self.updateLineEditsReadOnly)
        self.corrective_action_line_edit.textChanged.connect(self.updateLineEditsReadOnly)
        update_tree_widget(self.tree_widget, self.area_value_line_edit_short, self.area_value_line_edit_full,
                           self.line_value_line_edit_short, self.line_value_line_edit_full,
                           self.time_value_line_edit, self.machine_line_edit, self.problem_line_edit,
                           self.corrective_action_line_edit)
        tab2_buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("ADD")
        self.add_button.setShortcut("Ctrl+A")
        self.delete_button = QPushButton("DELETE")
        self.delete_button.setShortcut("Ctrl+D")
        self.add_button.clicked.connect(lambda: add_data_to_database(self.table_widget,
                                                                     self.area_value_line_edit_short,
                                                                     self.area_value_line_edit_full,
                                                                     self.line_value_line_edit_short,
                                                                     self.line_value_line_edit_full,
                                                                     self.time_value_line_edit,
                                                                     self.machine_line_edit,
                                                                     self.problem_line_edit,
                                                                     self.corrective_action_line_edit,
                                                                     self.tree_widget))

        self.delete_button.clicked.connect(
            lambda: remove_data_from_database(self.table_widget,
                                              self.area_value_line_edit_short, self.area_value_line_edit_full,
                                              self.line_value_line_edit_short,
                                              self.line_value_line_edit_full,
                                              self.time_value_line_edit,
                                              self.machine_line_edit,
                                              self.problem_line_edit,
                                              self.corrective_action_line_edit,
                                              self.tree_widget))
        area_layout.addWidget(self.area_label)
        area_layout.addWidget(self.area_value_line_edit_short)
        area_layout.addWidget(self.area_value_line_edit_full)
        line_layout.addWidget(self.line_label)
        line_layout.addWidget(self.line_value_line_edit_short)
        line_layout.addWidget(self.line_value_line_edit_full)
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.time_value_line_edit)
        machine_layout.addWidget(self.machine_label)
        machine_layout.addWidget(self.machine_line_edit)
        problem_layout.addWidget(self.problem_label)
        problem_layout.addWidget(self.problem_line_edit)
        corrective_action_layout.addWidget(self.corrective_action_label)
        corrective_action_layout.addWidget(self.corrective_action_line_edit)
        self.scroll_content_layout.addLayout(area_layout)
        self.scroll_content_layout.addLayout(line_layout)
        self.scroll_content_layout.addLayout(time_layout)
        self.scroll_content_layout.addLayout(machine_layout)
        self.scroll_content_layout.addLayout(problem_layout)
        self.scroll_content_layout.addLayout(corrective_action_layout)
        self.scroll_area_tab2.setWidget(self.scroll_content_widget)
        self.tab2_horizontal_layout.addWidget(self.tree_widget)
        self.tab2_horizontal_layout.addWidget(self.scroll_area_tab2)
        self.tab2_horizontal_layout.setStretchFactor(self.tree_widget, 3)
        self.tab2_horizontal_layout.setStretchFactor(self.scroll_area_tab2, 7)
        tab2_buttons_layout.addWidget(self.add_button)
        tab2_buttons_layout.addWidget(self.delete_button)
        self.tab2_layout.addLayout(self.tab2_horizontal_layout)
        self.tab2_layout.addLayout(tab2_buttons_layout)
        self.tab2_widget.setLayout(self.tab2_layout)
        self.tab_widget.addTab(self.tab2_widget, "Edit Variables")
        self.tree_widget_left = QTreeWidget()
        self.tree_widget_left.setStyleSheet(treeStyle)
        self.tree_widget_left.setSelectionMode(
            QAbstractItemView.MultiSelection)
        self.tree_widget_left.setHeaderHidden(True)
        for month in month_map.keys():
            month_item = QTreeWidgetItem(self.tree_widget_left)
            month_item.setText(0, month)
            for stat_header in stat_headers:
                category_item = QTreeWidgetItem(month_item)
                category_item.setText(0, stat_header)
        scroll_area_left = QScrollArea()
        scroll_area_left.setStyleSheet(statisticsStyle)
        scroll_area_left.setWidgetResizable(True)
        scroll_area_left.setWidget(self.tree_widget_left)
        self.tab3_scroll_area = QScrollArea()
        self.tab3_scroll_area.setStyleSheet(statisticsStyle)
        self.tab3_scroll_area.setWidgetResizable(True)
        layout_tab3_horizontal = QHBoxLayout()
        layout_tab3_horizontal.addWidget(self.tab3_scroll_area, 8)
        layout_tab3_horizontal.addWidget(scroll_area_left, 2)
        self.tab3_widget = QWidget()
        layout_tab3_vertical = QVBoxLayout()
        layout_tab3_vertical.addLayout(layout_tab3_horizontal)
        self.tab3_widget.setLayout(layout_tab3_vertical)
        self.tab_widget.addTab(self.tab3_widget, "View Statistics")
        self.layout.addWidget(self.tab_widget, 10)
        self.setStyleSheet(bodyStyle)
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        self.table_widget.cellActivated.connect(lambda row, col: edit_cell(self.table_widget, row, col))
        self.table_widget.itemChanged.connect(
            lambda item: validate_and_check_item(self.table_widget, item))
        self.table_widget.setSortingEnabled(True)
        delegate = CompleterDelegate(self.table_widget)
        self.table_widget.setItemDelegate(delegate)
        self.setLayout(self.layout)
        self.tab_widget.tabBarClicked.connect(lambda index: tab_changed(index, self.tab_widget, self))
        self.tab_widget.currentChanged.connect(lambda index: self.handleTabChange(index, table_menu, statistics_menu))
        self.tree_widget_left.itemSelectionChanged.connect(
            lambda: display_statistics(self.tree_widget_left, self.tab3_scroll_area))

    def handleTabChange(self, index, table_menu, statistics_menu):
        if index == 0:
            table_menu.setEnabled(True)
            for action in table_menu.actions():
                action.setEnabled(True)
            statistics_menu.setEnabled(False)
            for action in statistics_menu.actions():
                action.setEnabled(False)
        elif index == 2:
            table_menu.setEnabled(False)
            for action in table_menu.actions():
                action.setEnabled(False)
            statistics_menu.setEnabled(True)
            for action in statistics_menu.actions():
                action.setEnabled(True)
        else:
            table_menu.setEnabled(False)
            for action in table_menu.actions():
                action.setEnabled(False)
            statistics_menu.setEnabled(False)
            for action in statistics_menu.actions():
                action.setEnabled(False)

    def keyPressEvent(self, event):
        if self.tab_widget.currentIndex() != 0:
            super().keyPressEvent(event)
            return
        reply = QMessageBox()
        if event.matches(QKeySequence.Paste):
            reply.warning(self, "Paste Warning",
                          '<span style="font-size: 12pt;">Pasting values into cells is not allowed.</span>')
            return
        elif event.matches(QKeySequence.Undo):
            reply.warning(self, "Undo Warning",
                          '<span style="font-size: 12pt;">Retrieving previous values of cells is not allowed.</span>')
            return
        super().keyPressEvent(event)

    def copy_cells(self):
        selected_indexes = self.table_widget.selectedIndexes()
        if selected_indexes:
            selected_cells = [(index.row(), index.column()) for index in selected_indexes]
            selected_cells.sort()
            max_cells = 1000
            if len(selected_cells) > max_cells:
                reply = QMessageBox()
                reply.warning(self, "Copy Warning",
                              f'<span style="font-size: 12pt;">Copying {len(selected_cells)} cells may cause the application to freeze.</span>'
                              f'<span style="font-size: 12pt;">Please try copying a smaller selection.</span>')
                return
            copied_data = ""
            prev_row = selected_cells[0][0]
            for row, col in selected_cells:
                item = self.table_widget.item(row, col)
                if item:
                    if row != prev_row:
                        copied_data += "\n"
                        prev_row = row
                    cell_text = item.text()
                    copied_data += cell_text + "\t"
            clipboard = QApplication.clipboard()
            clipboard.setText(copied_data)

    def updateLineEditsReadOnly(self):
        if (not self.machine_line_edit.text() and
                not self.problem_line_edit.text() and
                not self.corrective_action_line_edit.text()):
            self.line_value_line_edit_short.setReadOnly(False)
            self.line_value_line_edit_full.setReadOnly(False)
            self.time_value_line_edit.setReadOnly(False)
        else:
            self.line_value_line_edit_short.setReadOnly(True)
            self.line_value_line_edit_full.setReadOnly(True)
            self.time_value_line_edit.setReadOnly(True)

    def closeEvent(self, event):
        if self.table_widget.rowCount() > 0:
            reply = QMessageBox()
            reply.setWindowTitle('Save Table?')
            reply.setText('<span style="font-size: 12pt;">Do you want to save the current table before closing?</span>')
            reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            buttons = reply.findChildren(QPushButton)
            for button in buttons:
                button.setMinimumWidth(100)
            button_yes = reply.button(QMessageBox.Yes)
            button_no = reply.button(QMessageBox.No)
            button_cancel = reply.button(QMessageBox.Cancel)
            button_yes.setText('Yes')
            button_no.setText('No')
            button_cancel.setText('Cancel')
            reply.exec_()
            if reply.clickedButton() == button_yes:
                save_table(self.table_widget)
                event.ignore()
            elif reply.clickedButton() == button_cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
