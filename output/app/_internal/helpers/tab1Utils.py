import json
import os
from datetime import datetime

import pandas as pd
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QTableWidgetItem, QDialog
)

from components.statisticsWindow import StatisticsDialog
from helpers.maps import column_headers
from helpers.tab3Tools import load_line_edit_values
from materials.styles import messageStyle

table_edited = False
df = None


def ask_statistic_values(tree_widget):
    global table_edited
    if not table_edited:
        dialog = StatisticsDialog()
        update_line_edits_from_json(dialog)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            line_edits = dialog.get_line_edits()
            num_days_1 = line_edits[0]
            num_days_2 = line_edits[1]
            num_days_3 = line_edits[2]
            num_days_4 = line_edits[3]
            num_days_5 = line_edits[4]
            num_days_6 = line_edits[5]
            num_days_7 = line_edits[6]
            num_days_8 = line_edits[7]
            num_days_9 = line_edits[8]
            num_days_10 = line_edits[9]
            num_days_11 = line_edits[10]
            num_days_12 = line_edits[11]
            if (num_days_1.isdigit() and num_days_2.isdigit() and num_days_3.isdigit() and num_days_4.isdigit()
                    and num_days_5.isdigit() and num_days_6.isdigit() and num_days_7.isdigit() and num_days_8.isdigit() and num_days_9.isdigit() and num_days_10.isdigit() and num_days_11.isdigit() and num_days_12.isdigit()):
                num_days_1 = int(num_days_1)
                num_days_2 = int(num_days_2)
                num_days_3 = int(num_days_3)
                num_days_4 = int(num_days_4)
                num_days_5 = int(num_days_5)
                num_days_6 = int(num_days_6)
                num_days_7 = int(num_days_7)
                num_days_8 = int(num_days_8)
                num_days_9 = int(num_days_9)
                num_days_10 = int(num_days_10)
                num_days_11 = int(num_days_11)
                num_days_12 = int(num_days_12)
                line_edits[0] = num_days_1
                line_edits[1] = num_days_2
                line_edits[2] = num_days_3
                line_edits[3] = num_days_4
                line_edits[4] = num_days_5
                line_edits[5] = num_days_6
                line_edits[6] = num_days_7
                line_edits[7] = num_days_8
                line_edits[8] = num_days_9
                line_edits[9] = num_days_10
                line_edits[10] = num_days_11
                line_edits[11] = num_days_12
            else:
                show_error_message("Please enter a valid number.")
            save_line_edit_values(line_edits)
            tree_widget.clearSelection()


def update_line_edits_from_json(dialog):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(os.path.dirname(current_dir), 'statistic_values.json')
    if os.path.exists(json_file_path):
        line_edits_from_json = load_line_edit_values(json_file_path)
        if line_edits_from_json:
            for line_edit, value in zip(dialog.line_edits, line_edits_from_json):
                line_edit.setText(str(value))


def save_line_edit_values(line_edits):
    data = {'line_edits': line_edits}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(os.path.dirname(current_dir), 'statistic_values.json')
    with open(json_file_path, 'w') as f:
        json.dump(data, f)


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
        if column_name == 'MONTH':
            try:
                month_value = int(item.text())
                if not (1 <= month_value <= 12):
                    show_error_message("Month value should be between 1 and 12.", table_widget)
                    item.setText("")
            except ValueError:
                show_error_message("Invalid month value. Please enter a number between 1 and 12.", table_widget)
                item.setText("")
            date_column_index = None
            for col in range(table_widget.columnCount()):
                if table_widget.horizontalHeaderItem(col).text().strip() == 'DATE':
                    date_column_index = col
                    break
            if date_column_index is not None:
                date_item = table_widget.item(item.row(), date_column_index)
                if date_item and date_item.text():
                    date_value = datetime.strptime(date_item.text(), '%d-%m-%Y').month
                    entered_month = int(item.text())
                    if date_value != entered_month:
                        show_error_message("Month value in DATE does not match MONTH value. Please correct the values.",
                                           table_widget)
                        item.setText("")
        if column_name == 'DATE':
            try:
                pd.to_datetime(item.text(), format='%d-%m-%Y')
            except ValueError:
                show_error_message("Invalid date format. Please enter date in DD-MM-YYYY format.", table_widget)
                item.setText("")
                return
            month_column_index = None
            for col in range(table_widget.columnCount()):
                if table_widget.horizontalHeaderItem(col).text().strip() == 'MONTH':
                    month_column_index = col
                    break
            if month_column_index is not None:
                month_item = table_widget.item(item.row(), month_column_index)
                if month_item and month_item.text():
                    month_value = int(month_item.text())
                    entered_month = datetime.strptime(item.text(), '%d-%m-%Y').month
                    if month_value != entered_month:
                        show_error_message("Month value in DATE does not match MONTH value. Please correct the values.",
                                           table_widget)
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
    if col == 7:
        line_item = table_widget.item(item.row(), 8)
        if line_item:
            line_item.setText("")
    elif col == 8:
        machine_item = table_widget.item(item.row(), 9)
        if machine_item:
            machine_item.setText("")
    elif col == 9:
        problem_item = table_widget.item(item.row(), 10)
        if problem_item:
            problem_item.setText("")
    elif col == 10:
        status_item = table_widget.item(item.row(), 11)
        if status_item:
            status_item.setText("")
    elif col == 11:
        incharge_item = table_widget.item(item.row(), 12)
        if incharge_item:
            incharge_item.setText("")
    elif col == 12:
        caction_item = table_widget.item(item.row(), 13)
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
        QMessageBox.information(main_window, "Tab Disabled", "Please open an Excel file to access this tab.")
    if index == 2 and table_edited:
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


def load_excel_file(right_line_edit, file_path, table_widget, tab_widget):
    global df
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            df.loc[0] = ''
        else:
            total_time_column = [col for col in df.columns if col.strip() == 'TOTAL TIME']
            if total_time_column:
                df[total_time_column[0]] = df[total_time_column[0]].fillna(0).astype(str).replace('', '0')
        month_column = [col for col in df.columns if col.strip() == 'MONTH']
        date_column = [col for col in df.columns if col.strip() == 'DATE']
        if month_column and date_column:
            try:
                df['MONTH'] = df['MONTH'].astype(int)
                df[date_column[0]] = pd.to_datetime(df[date_column[0]], format='%d-%m-%Y')
                df['MONTH_FROM_DATE'] = df[date_column[0]].dt.month
                invalid_months = df[df['MONTH'] != df['MONTH_FROM_DATE']]
                if not invalid_months.empty:
                    show_error_message("Invalid month value found in MONTH column. The month value does not match "
                                       "the month part of the date in the DATE column. Please correct the values.")
                    for index, _ in invalid_months.iterrows():
                        table_widget.setItem(index, df.columns.get_loc('MONTH'), QTableWidgetItem(''))
                    return
            except ValueError:
                show_error_message("Invalid month value found in MONTH column. Please ensure all values are "
                                   "whole numbers between 1 and 12.")
                return
        if 'MONTH_FROM_DATE' in df.columns:
            df.drop(columns=['MONTH_FROM_DATE'], inplace=True)
        if date_column:
            df[date_column[0]] = pd.to_datetime(df[date_column[0]]).dt.strftime('%d-%m-%Y')
        time_columns = [col for col in df.columns if col.strip() in ['TIME', 'CLOSING TIME']]
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
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
    total_time_column = [col for col in df.columns if col.strip() == 'TOTAL TIME']
    if total_time_column:
        df[total_time_column[0]] = pd.to_numeric(df[total_time_column[0]], errors='coerce').fillna(0).astype(int)
    df = df.fillna('')
    populate_table_widget_from_excel(table_widget, df)
    tab_widget.setTabEnabled(1, True)
    tab_widget.setTabEnabled(2, True)
    right_line_edit.setText(os.path.basename(file_path))
    right_line_edit.show()


def open_table(right_line_edit, table_widget, tab_widget):
    if table_edited:
        reply = QMessageBox().question(
            None, 'Save Changes', 'Do you want to save changes before opening a new file?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        print("t2")
        if reply == QMessageBox.Save:
            print("t1")
            save_table(table_widget)
            return
        elif reply == QMessageBox.Cancel:
            return
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Open Excel File", "", "Excel Files (*.xlsx)", options=options
    )
    if file_path:
        load_excel_file(right_line_edit, file_path, table_widget, tab_widget)


def new_table(right_line_edit, table_widget, tab_widget, image_label):
    global table_edited, df
    if table_edited:
        reply = QMessageBox.question(None, 'Save Table?',
                                     'Do you want to save the current table before clearing it?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            save_table(table_widget)
            return
        elif reply == QMessageBox.Cancel:
            return
    table_widget.setRowCount(0)
    right_line_edit.clear()
    right_line_edit.hide()
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(None, "Create Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_path:
        try:
            df = pd.DataFrame(columns=[table_widget.horizontalHeaderItem(j).text()
                                       for j in range(table_widget.columnCount())])
            df.loc[0] = ''
            df.to_excel(file_path, index=False)
            right_line_edit.setText(os.path.basename(file_path))
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
