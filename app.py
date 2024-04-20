import sys

from PyQt5.QtWidgets import (QApplication, QTabWidget, QSplitter, QScrollArea, QTreeWidget, QTreeWidgetItem)

from components.cdelegate import CompleterDelegate
from helpers.p1utils import *
from styles import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt Window')
        self.setGeometry(100, 100, 1280, 720)
        # Set a minimum size for the window
        self.setMinimumSize(1280, 720)
        # self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Header
        self.header_label = QLabel("Machine Analysis Application")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet(headerStyle)
        self.layout.addWidget(self.header_label, 1)

        # Body - Tab Widget
        self.tab_widget = QTabWidget()

        # Data Entry tab
        self.data_entry_tab = QWidget()
        self.data_entry_layout = QVBoxLayout(self.data_entry_tab)

        # Splitter for the left and right side
        self.splitter = QSplitter(Qt.Horizontal)

        # Right side (table widget)
        self.right_layout = QVBoxLayout()
        self.right_line_edit = QLineEdit()
        self.right_layout.addWidget(self.right_line_edit)
        self.table_widget = QTableWidget()
        self.column_headers = ["Date", "Time", "AM/PM", "Closing Time", "AM/PM", "Total Time", "Area",
                               "Line", "Machine", "Problem", "Status", "Incharge", "Corrective Action"]
        self.table_widget.setColumnCount(len(self.column_headers))
        self.table_widget.setHorizontalHeaderLabels(self.column_headers)
        self.table_widget.setStyleSheet(tableStyle)
        self.right_layout.addWidget(self.table_widget)

        # Enable word wrap for the “Corrective Action” column
        self.table_widget.setColumnWidth(12, 200)
        self.table_widget.horizontalHeader().setSectionResizeMode(12, QHeaderView.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(12, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        # Set word wrap for items in the “Corrective Action” column
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 12)
            if item:
                item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

        # Set the height of each row to accommodate wrapped text
        self.table_widget.resizeRowsToContents()

        # Button group
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("SAVE")
        self.open_button = QPushButton("OPEN")
        self.new_button = QPushButton("NEW")
        self.open_button.clicked.connect(
            lambda: open_table(self.tab3_scroll_area, self.table_widget,
                               self.right_line_edit, self.tab_widget))
        self.open_button.setShortcut("Ctrl+O")
        self.new_button.clicked.connect(
            lambda: new_table(self.tab3_scroll_area, self.table_widget,
                              self.right_line_edit, self.tab_widget))
        self.new_button.setShortcut("Ctrl+N")
        self.save_button.clicked.connect(lambda: save_table(self.table_widget))
        self.save_button.setShortcut("Ctrl+S")
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.open_button)
        self.button_layout.addWidget(self.new_button)
        self.right_layout.addLayout(self.button_layout)

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        self.splitter.addWidget(self.right_widget)
        self.splitter.setStretchFactor(1, 7)

        self.data_entry_layout.addWidget(self.splitter)
        self.data_entry_tab.setLayout(self.data_entry_layout)

        self.tab_widget.addTab(self.data_entry_tab, "Edit Table")

        # Create a new tab widget for 'Tab 2'
        self.tab2_widget = QWidget()

        # Create layouts and widgets for 'Tab 2' content
        self.tab2_layout = QVBoxLayout()  # Vertical layout for 'Tab 2'
        self.tab2_horizontal_layout = QHBoxLayout()  # A horizontal layout for tree widget and scroll area

        # Create a tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet(treeStyle)
        self.tree_widget.setHeaderHidden(True)  # Hide the header

        # Add top-level items
        overall_plant_item = QTreeWidgetItem(["Overall Plant"])
        shox_item = QTreeWidgetItem(["SHOX"])
        fff_item = QTreeWidgetItem(["FFFA"])
        ot_cell_item = QTreeWidgetItem(["OT CELL"])
        it_grd_item = QTreeWidgetItem(["IT GRD"])

        # Add child items to "SHOX"
        shox_item.addChild(QTreeWidgetItem(["DA-1"]))
        shox_item.addChild(QTreeWidgetItem(["DA-2"]))
        shox_item.addChild(QTreeWidgetItem(["DA-3"]))
        shox_item.addChild(QTreeWidgetItem(["DA-4"]))
        shox_item.addChild(QTreeWidgetItem(["DA-5"]))
        shox_item.addChild(QTreeWidgetItem(["DA-7"]))
        shox_item.addChild(QTreeWidgetItem(["DA-9"]))
        shox_item.addChild(QTreeWidgetItem(["DA-10"]))
        shox_item.addChild(QTreeWidgetItem(["DA-11"]))
        shox_item.addChild(QTreeWidgetItem(["Valve Assly"]))

        # Add child items to "FFFA"
        fff_item.addChild(QTreeWidgetItem(["FA-1"]))
        fff_item.addChild(QTreeWidgetItem(["FA-2"]))
        fff_item.addChild(QTreeWidgetItem(["FA-3"]))
        fff_item.addChild(QTreeWidgetItem(["FA-4"]))
        fff_item.addChild(QTreeWidgetItem(["FA-5"]))
        fff_item.addChild(QTreeWidgetItem(["FA-6"]))
        fff_item.addChild(QTreeWidgetItem(["FA-7"]))
        fff_item.addChild(QTreeWidgetItem(["TFF-1"]))
        fff_item.addChild(QTreeWidgetItem(["TFF-2"]))

        # Add child items to “OT CELL”
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-1"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-2"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-3"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-4"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-5"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-6"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-7"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-8"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-9"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-10"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-11"]))
        ot_cell_item.addChild(QTreeWidgetItem(["Cell-12"]))

        # Add child items to "IT GRD"
        it_grd_item.addChild(QTreeWidgetItem(["ITG-2"]))
        it_grd_item.addChild(QTreeWidgetItem(["ITG-1"]))

        # Add top-level and child items to the tree widget
        overall_plant_item.addChild(shox_item)
        overall_plant_item.addChild(fff_item)
        overall_plant_item.addChild(ot_cell_item)
        overall_plant_item.addChild(it_grd_item)
        self.tree_widget.addTopLevelItem(overall_plant_item)

        # Connect signals to slots for handling tree widget item selection changes.
        self.tree_widget.itemClicked.connect(self.update_labels)

        # Create a scroll area for additional content in 'Tab 2'
        self.scroll_area_tab2 = QScrollArea()
        self.scroll_area_tab2.setStyleSheet(scrollStyle)
        self.scroll_area_tab2.setWidgetResizable(True)

        # Create a widget to contain the content of the scroll area.
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)

        # Add labels and line edits for the desired fields
        self.area_label = QLabel("Area:")
        self.area_value_label = QLabel()  # This will display the selected area from the tree widget
        self.line_label = QLabel("Line:")
        self.line_value_label = QLabel()  # This will display the selected line from the tree widget
        self.machine_label = QLabel("Machine:")
        self.machine_line_edit = QLineEdit()
        self.problem_label = QLabel("Problem:")
        self.problem_line_edit = QLineEdit()
        self.corrective_action_label = QLabel("Corrective Action:")
        self.corrective_action_line_edit = QLineEdit()

        # Add the widgets to the scroll content layout
        self.scroll_content_layout.addWidget(self.area_label)
        self.scroll_content_layout.addWidget(self.area_value_label)
        self.scroll_content_layout.addWidget(self.line_label)
        self.scroll_content_layout.addWidget(self.line_value_label)
        self.scroll_content_layout.addWidget(self.machine_label)
        self.scroll_content_layout.addWidget(self.machine_line_edit)
        self.scroll_content_layout.addWidget(self.problem_label)
        self.scroll_content_layout.addWidget(self.problem_line_edit)
        self.scroll_content_layout.addWidget(self.corrective_action_label)
        self.scroll_content_layout.addWidget(self.corrective_action_line_edit)

        # Set the content widget of the scroll area
        self.scroll_area_tab2.setWidget(self.scroll_content_widget)

        # Add the scroll area to the horizontal layout
        self.tab2_horizontal_layout.addWidget(self.tree_widget)
        self.tab2_horizontal_layout.addWidget(self.scroll_area_tab2)

        # Set the stretch factors for the tree widget and scroll area.
        self.tab2_horizontal_layout.setStretchFactor(self.tree_widget, 3)
        self.tab2_horizontal_layout.setStretchFactor(self.scroll_area_tab2, 7)

        # Set the tab2_horizontal_layout as the layout for 'Tab 2'
        self.tab2_layout.addLayout(self.tab2_horizontal_layout)

        self.tab2_widget.setLayout(self.tab2_layout)

        self.tab_widget.addTab(self.tab2_widget, "Edit Variables")

        # Data Statistics tab
        self.tab3_scroll_area = QScrollArea()
        self.tab3_scroll_area.setStyleSheet(statisticsStyle)
        self.tab3_scroll_area.setWidgetResizable(True)

        # Button for saving data
        self.save_button_tab3 = QPushButton("Save")

        # Layout for buttons below the QTextEdit
        self.button_layout_tab3 = QHBoxLayout()
        self.button_layout_tab3.addWidget(self.save_button_tab3)
        self.button_layout_tab3.setAlignment(Qt.AlignRight)

        # Layout for the tab including the buttons
        self.layout_tab3 = QVBoxLayout()
        self.layout_tab3.addWidget(self.tab3_scroll_area)
        self.layout_tab3.addLayout(self.button_layout_tab3)

        self.tab3_widget = QWidget()
        self.tab3_widget.setLayout(self.layout_tab3)

        self.tab_widget.addTab(self.tab3_widget, "View Statistics")

        self.layout.addWidget(self.tab_widget, 8)
        self.setStyleSheet(bodyStyle)

        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)

        self.table_widget.cellActivated.connect(lambda row, col: edit_cell(self.table_widget, row, col))

        self.table_widget.itemChanged.connect(lambda item: validate_item(item, self.table_widget))

        self.table_widget.setSortingEnabled(True)

        delegate = CompleterDelegate(self.table_widget)
        self.table_widget.setItemDelegate(delegate)

        self.table_widget.itemChanged.connect(lambda item: self.check_cell(item))

        # Footer
        self.footer_label = QLabel("Internship Project - S.P Ashvath")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet(footerStyle)
        self.layout.addWidget(self.footer_label, 1)

        self.setLayout(self.layout)

    # Add a new method to your MainWindow class to handle the validation and adding new rows.
    def check_cell(self, item):
        # Get the current row and column of the edited item
        row = item.row()

        # Check if the edited cell is in the last row
        if row == self.table_widget.rowCount() - 1:
            # Check if any cell in the row contains data
            for j in range(self.table_widget.columnCount()):
                cell_data = self.table_widget.item(row, j)
                if cell_data and cell_data.text():
                    # If any cell in the row contains data, add a new row and break out of the loop.
                    self.add_new_row()
                    break

    # Add a new method to your MainWindow class to add a new row to the table widget.
    def add_new_row(self):
        # Insert a new row at the end of the table widget.
        row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(row_count)

        # Set default values for the cells in the new row
        for col in range(self.table_widget.columnCount()):
            item = QTableWidgetItem("")
            self.table_widget.setItem(row_count, col, item)

    # Define a slot to update the labels when a tree widget item is clicked.
    def update_labels(self, item):
        # Check if the clicked item has a parent (i.e., it is a child item)
        if item.parent():
            # Get the text of the parent item (e.g., "SHOX", "FFFA", etc.)
            parent_text = item.parent().text(0)
            # Get the text of the selected item (e.g., "DA-1", "FA-1", etc.)
            item_text = item.text(0)
            # Update the labels with the parent and item texts
            self.area_value_label.setText(parent_text)
            self.line_value_label.setText(item_text)

    def closeEvent(self, event):
        if self.table_widget.rowCount() > 0:  # Check if the table is not empty
            reply = QMessageBox()
            reply.setStyleSheet("""
                font-family: Century Gothic;
                font-size: 18px;
            """)
            reply.setWindowTitle('Save Table?')
            reply.setText('Do you want to save the current table before closing?')
            reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            # Adjust button sizes
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
                # Save the table
                save_table(self.table_widget)
                event.accept()
            elif reply.clickedButton() == button_cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet(windowStyle)
    window.showMaximized()  # Maximize the window
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()