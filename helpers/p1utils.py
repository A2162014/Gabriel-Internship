import os
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from helpers.p3tools import *


def edit_cell(table_widget, row, col):
    """Edit the cell at the specified row and column in the table widget."""
    item = table_widget.item(row, col)
    if item:
        table_widget.editItem(item)


def validate_date_format(date_str):
    """Validate the date format (DD-MM-YYYY)."""
    try:
        pd.to_datetime(date_str, format='%d-%m-%Y')
        return True
    except ValueError:
        return False


def validate_float_format(float_str):
    """Validate the float format."""
    try:
        float(float_str)
        return True
    except ValueError:
        return False


def validate_int_format(int_str):
    """Validate the integer format."""
    try:
        int(int_str)
        return True
    except ValueError:
        return False


def show_error_message(message, parent):
    """Show an error message dialog."""
    QMessageBox.warning(parent, "Error", message)


def validate_item(item, table_widget):
    """Validate the item in the table widget."""
    column_name = table_widget.horizontalHeaderItem(item.column()).text().strip()
    if item.text():
        if column_name == 'DATE':
            if not validate_date_format(item.text()):
                show_error_message("Invalid date format. Please enter date in DD-MM-YYYY format.", table_widget)
                item.setText("")  # Clear the invalid value
        elif column_name == 'TOTAL TIME':
            if not validate_int_format(item.text()):
                show_error_message("Invalid total time format. Please enter a whole number.", table_widget)
                item.setText("")  # Clear the invalid value
        elif column_name in ['TIME', 'CLOSING TIME']:
            if not validate_float_format(item.text()):
                show_error_message("Invalid float format. Please enter a number with up to 2 decimal points.",
                                   table_widget)
                item.setText("")  # Clear the invalid value
        elif column_name == 'INCHARGE':
            if not all(char.isalpha() for char in item.text()):
                show_error_message("Invalid characters in INCHARGE column. Only alphabets are allowed.", table_widget)
                item.setText("")  # Clear the invalid value


def populate_table_widget_from_excel(table_widget, df):
    """Populate the table widget with data from an Excel file."""
    num_rows, num_cols = df.shape
    table_widget.setRowCount(num_rows + 1)  # Add an empty row
    table_widget.setColumnCount(num_cols)
    table_widget.setHorizontalHeaderLabels(df.columns)
    for i in range(num_rows):
        for j in range(num_cols):
            item = QTableWidgetItem(str(df.iat[i, j]))
            table_widget.setItem(i, j, item)
    table_widget.setCurrentCell(0, 0)


def open_table(tab3_scroll_area, table_widget, line_edit, tab_widget):
    """
    Open an Excel file and populate the table widget with its data.
    """
    # Check if any cell has been edited
    changes_made = False
    for row in range(table_widget.rowCount()):
        for col in range(table_widget.columnCount()):
            item = table_widget.item(row, col)
            if item is not None and item.text() != "":
                changes_made = True
                break
        if changes_made:
            break

    if changes_made:
        reply = QMessageBox.question(None, 'Save Changes', 'Do you want to save changes before opening a new file?',
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if reply == QMessageBox.Save:
            # Save the changes
            save_table(table_widget)
        elif reply == QMessageBox.Cancel:
            return

    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Open Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_path:
        # Read the Excel file
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error reading Excel file: {str(e)}")
            return

        # Check if the Excel file has only one sheet
        if len(pd.ExcelFile(file_path).sheet_names) != 1:
            QMessageBox.warning(None, "Warning", "Please select an Excel file with only one sheet.")
            return

        df.rename(columns={'AM/PM.1': 'AM/PM'}, inplace=True)
        stripped_columns = [col.strip() for col in df.columns]

        # Check if the Excel file has the required column headings
        missing_columns = [col for col in column_headers if col not in stripped_columns]
        if missing_columns:
            QMessageBox.warning(None, "Warning",
                                f"The Excel file is missing the following columns: \n{', '.join(missing_columns)}")
            return

        # Check if there are any repetitive columns
        if len(column_headers) != len(stripped_columns):
            QMessageBox.warning(None, "Warning",
                                "The Excel file contains repetitive column headings. Please ensure each column heading is unique.")
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
            df[total_time_column[0]] = df[total_time_column[0]].fillna(0).astype(int)

        df = df.where(pd.notnull(df), '')  # Replace NaN values with empty strings

        populate_table_widget_from_excel(table_widget, df)

        tab_widget.setTabEnabled(1, True)
        tab_widget.setTabEnabled(2, True)

        # Update the line edit with the file name
        line_edit.setText(os.path.basename(file_path))

        num_working_days = None
        while num_working_days is None:
            dialog = WorkingDaysDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                w_line_edit = dialog.get_line_edit()
                num_days = w_line_edit.text()
                if num_days.isdigit():
                    num_working_days = int(num_days)
                else:
                    QMessageBox.warning(dialog, "Warning", "Please enter a valid number.")

        add_widgets_to_scroll_area(tab3_scroll_area, line_edit, df, num_working_days)


def new_table(table_widget, line_edit, tab_widget):
    """Create a new table and populate it with data from an Excel file."""
    if table_widget.rowCount() > 0:
        reply = QMessageBox.question(None, 'Save Table?',
                                     'Do you want to save the current table before clearing it?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            save_table(table_widget)
        elif reply == QMessageBox.Cancel:
            return

    table_widget.clearContents()
    table_widget.setRowCount(0)
    line_edit.clear()

    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_path:
        df = pd.DataFrame(
            columns=[table_widget.horizontalHeaderItem(j).text() for j in range(table_widget.columnCount())])
        df.to_excel(file_path, index=False)
        QMessageBox.information(None, 'New Table Created', f'New empty table created and saved to {file_path}.')
        line_edit.setText(os.path.basename(file_path))

        df_new = pd.read_excel(file_path)
        df_new.rename(columns={'AM/PM.1': 'AM/PM'}, inplace=True)
        populate_table_widget_from_excel(table_widget, df_new)

        tab_widget.setTabEnabled(1, True)
        tab_widget.setTabEnabled(2, False)


def save_table(table_widget):
    """Save the table to an Excel file."""
    if table_widget.rowCount() == 0:
        QMessageBox.warning(None, 'Empty Table', 'The table is empty. There is nothing to save.')
        return

    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_path:
        df = pd.DataFrame(
            columns=[table_widget.horizontalHeaderItem(j).text() for j in range(table_widget.columnCount())])
        for i in range(table_widget.rowCount()):
            row_data = []
            for j in range(table_widget.columnCount()):
                item = table_widget.item(i, j)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            df.loc[i] = row_data
        df.to_excel(file_path, index=False)
        QMessageBox.information(None, 'Table Saved', f'Table saved to {file_path}.')
