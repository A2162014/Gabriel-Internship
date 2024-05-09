import os

import pandas as pd
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QTableWidgetItem, QDialog
)

from components.spopup import StatisticsDialog
from helpers.p3tools import add_widgets_to_scroll_area
from maps import column_headers
from styles import messageStyle

table_edited = False
df = None


def ask_statistic_values(index, tab3_scroll_area, line_edit):
    global df
    if index == 2:
        print("t3")
        num_working_days = None
        while num_working_days is None:
            dialog = StatisticsDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                line_edits = dialog.get_line_edits()
                num_days = line_edits[0]
                if num_days.isdigit():
                    num_working_days = int(num_days)
                else:
                    show_error_message("Please enter a valid number.")
        add_widgets_to_scroll_area(tab3_scroll_area, line_edit, df, num_working_days, line_edits)


def edit_cell(table_widget, row, col):
    item = table_widget.item(row, col)
    if item:
        table_widget.editItem(item)


def show_error_message(message, parent=None):
    error_dialog = QMessageBox(parent)
    error_dialog.setStyleSheet(messageStyle)
    error_dialog.warning(parent, "Error", message)


def validate_and_check_item(table_widget, item):
    global table_edited
    table_edited = True
    column_name = table_widget.horizontalHeaderItem(item.column()).text().strip()
    if item.text():
        if column_name == 'DATE':
            try:
                pd.to_datetime(item.text(), format='%d-%m-%Y')
            except ValueError:
                show_error_message("Invalid date format. Please enter date in DD-MM-YYYY format.", table_widget)
                item.setText("")
        elif column_name == 'TOTAL TIME':
            if not item.text().isdigit():
                show_error_message("Invalid total time format. Please enter a whole number.", table_widget)
                item.setText("")
        elif column_name in ['TIME', 'CLOSING TIME']:
            try:
                float(item.text())
            except ValueError:
                show_error_message("Invalid float format. Please enter a number with up to 2 decimal points.",
                                   table_widget)
                item.setText("")
        elif column_name == 'INCHARGE':
            if not item.text().isalpha():
                show_error_message("Invalid characters in INCHARGE column. Only alphabets are allowed.",
                                   table_widget)
                item.setText("")
    col = item.column()
    if col == 6:
        line_item = table_widget.item(item.row(), 7)
        if line_item:
            line_item.setText("")
    elif col == 7:
        machine_item = table_widget.item(item.row(), 8)
        if machine_item:
            machine_item.setText("")
    elif col == 8:
        problem_item = table_widget.item(item.row(), 9)
        if problem_item:
            problem_item.setText("")
    elif col == 9:
        caction_item = table_widget.item(item.row(), 12)
        if caction_item:
            caction_item.setText("")
    row = item.row()
    column_count = table_widget.columnCount()
    if row == table_widget.rowCount() - 1:
        for j in range(column_count):
            cell_data = table_widget.item(row, j)
            if cell_data and cell_data.text():
                table_widget.insertRow(row + 1)
                return


def tab_changed(index, tab_widget, main_window):
    global table_edited
    if not tab_widget.isTabEnabled(index):
        print("t1")
        QMessageBox.information(main_window, "Tab Disabled", "Please open an Excel file to access this tab.")
    if index == 2 and table_edited:
        print("t2")
        reply = QMessageBox()
        reply.setStyleSheet(messageStyle)
        reply.warning(main_window, "Table Edited",
                      "The table has been edited. Please reopen the changed file to view updated statistics.",
                      QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            pass
        else:
            return


def populate_table_widget_from_excel(table_widget, df):
    global table_edited
    table_widget.setRowCount(df.shape[0])
    table_widget.setColumnCount(df.shape[1])
    table_widget.setHorizontalHeaderLabels(df.columns)
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            item = QTableWidgetItem(str(df.iloc[i, j]))
            table_widget.setItem(i, j, item)
            table_edited = False
    table_widget.setCurrentCell(0, 0)


def load_excel_file(file_path, table_widget, line_edit, tab_widget):
    global df
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            df.loc[0] = ''
        else:
            total_time_column = [col for col in df.columns if col.strip() == 'TOTAL TIME']
            if total_time_column:
                df[total_time_column[0]] = df[total_time_column[0]].fillna(0).astype(str).replace('', '0')
    except Exception as e:
        show_error_message(f"Error reading Excel file: {str(e)}")
        return
    if len(pd.ExcelFile(file_path).sheet_names) != 1:
        show_error_message("Please select an Excel file with only one sheet.")
        return
    df.rename(columns={'AM/PM.1': 'AM/PM'}, inplace=True)
    stripped_columns = [col.strip() for col in df.columns]
    missing_columns = [col for col in column_headers if col not in stripped_columns]
    if missing_columns:
        show_error_message(
            f"The Excel file is missing the following columns: {', '.join(missing_columns)}"
        )
        return
    if len(column_headers) != len(stripped_columns):
        show_error_message(
            "The Excel file contains repetitive column headings. Please ensure each column heading is unique."
        )
        return
    date_column = [col for col in df.columns if col.strip() == 'DATE']
    if date_column:
        df[date_column[0]] = pd.to_datetime(df[date_column[0]]).dt.strftime('%d-%m-%Y')
    time_columns = [col for col in df.columns if col.strip() in ['TIME', 'CLOSING TIME']]
    for col in time_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
    total_time_column = [col for col in df.columns if col.strip() == 'TOTAL TIME']
    if total_time_column:
        df[total_time_column[0]] = pd.to_numeric(df[total_time_column[0]], errors='coerce').fillna(0).astype(int)
    df = df.fillna('')
    populate_table_widget_from_excel(table_widget, df)
    tab_widget.setTabEnabled(1, True)
    tab_widget.setTabEnabled(2, True)
    line_edit.setText(os.path.basename(file_path))


def open_table(table_widget, line_edit, tab_widget):
    changes_made = any(
        table_widget.item(row, col) is not None and table_widget.item(row, col).text() != ""
        for row in range(table_widget.rowCount())
        for col in range(table_widget.columnCount())
    )
    if changes_made:
        reply = QMessageBox()
        reply.setStyleSheet(messageStyle)
        reply.question(
            None, 'Save Changes', 'Do you want to save changes before opening a new file?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        if reply == QMessageBox.Save:
            save_table(table_widget)
        elif reply == QMessageBox.Cancel:
            return
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Open Excel File", "", "Excel Files (*.xlsx)", options=options
    )
    if file_path:
        load_excel_file(file_path, table_widget, line_edit, tab_widget)


def new_table(table_widget, line_edit, tab_widget):
    global table_edited, df
    if table_edited:
        reply = QMessageBox.question(None, 'Save Table?',
                                     'Do you want to save the current table before clearing it?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            save_table(table_widget)
        elif reply == QMessageBox.Cancel:
            return
    table_widget.setRowCount(0)
    line_edit.clear()
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_path:
        try:
            df = pd.DataFrame(columns=[table_widget.horizontalHeaderItem(j).text()
                                       for j in range(table_widget.columnCount())])
            df.loc[0] = ''
            df.to_excel(file_path, index=False)
            line_edit.setText(os.path.basename(file_path))
            populate_table_widget_from_excel(table_widget, df)
            QMessageBox.information(None, 'New Table Created', f'New empty table created and saved to {file_path}.')
            tab_widget.setTabEnabled(1, True)
            tab_widget.setTabEnabled(2, False)
            table_edited = False
        except Exception as e:
            show_error_message(f'Error saving table: {e}')


def save_table(table_widget):
    global df
    if table_widget.rowCount() == 0:
        show_error_message('The table is empty. There is nothing to save.')
        return
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        None, "Save Excel File", "", "Excel Files (*.xlsx)", options=options
    )
    if file_path:
        try:
            df = pd.DataFrame(
                [[table_widget.item(i, j).text() if table_widget.item(i, j) is not None else ""
                  for j in range(table_widget.columnCount())]
                 for i in range(table_widget.rowCount())],
                columns=[table_widget.horizontalHeaderItem(j).text()
                         for j in range(table_widget.columnCount())]
            )
            df.to_excel(file_path, index=False)
            show_error_message(f'Table saved to {file_path}.')
        except Exception as e:
            show_error_message(f'Error saving table: {e}')
