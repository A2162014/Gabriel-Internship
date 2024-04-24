import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog, QMessageBox, QLineEdit, QLabel, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from maps import *


def get_area_for_line(line):
    for area, lines in area_line_map_table.items():
        if line in lines:
            return area
    return None


def calculate_bd_time_percentage(file_path, working_days):
    """
    Calculate B/D Time percentage for each line in the Excel file.

    Parameters:
        file_path (str): Path to the Excel file.
        working_days (int): Number of working days.

    Returns:
        dict: Dictionary containing B/D Time percentages for each line.
    """
    # Read Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Filter lines based on the location "SHOX"
    lines = area_line_map_table.get("SHOX", [])
    print(f"lines {lines}")

    bd_percentages = {}
    for line in lines:
        df_line = df[df['LINE'].str.contains(line, case=False)]
        print(f"df_line {df_line}")

        # Calculate sum of total time for line
        line_total_sum = df_line[df_line['LINE'] == line]["TOTAL TIME"].sum()
        print(f"line_total_sum {line_total_sum}")

        # Get the availability time for the line
        area = get_area_for_line(line)
        line_avail_time = time_availability.get(area, {}).get(line, 0)
        print(f"line_avail_time {line_avail_time}")

        # Calculate B/D Time percentage for line
        line_bd_time_percentage = (line_total_sum / (line_avail_time * working_days)) * 100
        bd_percentages[line] = line_bd_time_percentage

    print(f"bd_percentages {bd_percentages}")

    return bd_percentages


def update_table_and_plot(bd_percentages, table_widget, plot_canvas):
    """
    Update table widget and plot graph with B/D Time percentages.

    Parameters:
        bd_percentages (dict): Dictionary containing B/D Time percentages for each line.
        table_widget (QTableWidget): Table widget to display the data.
        plot_canvas (FigureCanvas): Canvas to display the plot.
    """
    # Update table widget
    table_widget.setRowCount(len(bd_percentages))
    for row, (line, percentage) in enumerate(bd_percentages.items()):
        table_widget.setItem(row, 0, QTableWidgetItem(line))
        table_widget.setItem(row, 1, QTableWidgetItem(f"{percentage:.2f}%"))
        table_widget.setItem(row, 2, QTableWidgetItem("1%"))  # Target in %

    # Plot graph
    plt.figure(figsize=(8, 6))
    lines, percentages = zip(*bd_percentages.items())
    plt.bar(lines, percentages, color='skyblue')
    plt.xlabel('Location')
    plt.ylabel('% of B/D')
    plt.title('B/D Time Percentage')
    plt.xticks(rotation=45, ha='right')

    # Set y-axis range and draw red line at y = 1
    plt.ylim(0, 1.2)
    plt.axhline(y=1, color='red', linestyle='--')

    plot_canvas.figure = plt.gcf()
    plot_canvas.draw()


def handle_open_file(line_edit):
    """
    Handle opening of Excel file.

    Parameters:
        line_edit (QLineEdit): Line edit widget for file path input.
    """
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(None, "Open Excel File", "", "Excel Files (*.xls *.xlsx)",
                                               options=options)
    if file_name:
        line_edit.clear()
        line_edit.setText(file_name)
    else:
        QMessageBox.warning(None, 'No File Selected', 'No Excel file selected.')


def handle_calculate_bd_time_percentage(line_edit, working_days_edit, table_widget, plot_canvas):
    """
    Handle calculation of B/D Time percentages.

    Parameters:
        line_edit (QLineEdit): Line edit widget for file path input.
        working_days_edit (QLineEdit): Line edit widget for working days input.
        table_widget (QTableWidget): Table widget to display the data.
        plot_canvas (FigureCanvas): Canvas to display the plot.
    """
    file_path = line_edit.text()
    if not file_path:
        QMessageBox.warning(None, 'No File Selected', 'No Excel file selected.')
        return

    working_days_str = working_days_edit.text()
    if not working_days_str.isdigit():
        QMessageBox.warning(None, 'Invalid Input', 'Please enter a valid number of working days.')
        return

    working_days = int(working_days_str)

    # Calculate B/D Time percentage for each line
    bd_percentages = calculate_bd_time_percentage(file_path, working_days)

    # Update table widget and plot canvas
    update_table_and_plot(bd_percentages, table_widget, plot_canvas)


def main():
    app = QApplication([])

    main_window = QMainWindow()
    main_window.setWindowTitle("Excel B/D Time Percentage Calculator")

    tab_widget = QTabWidget()

    # Tab 1: Open Excel File
    tab_1 = QWidget()
    layout_1 = QVBoxLayout(tab_1)

    line_edit = QLineEdit()
    line_edit.setPlaceholderText("Excel File Path")

    open_button = QPushButton("Open Excel File")
    open_button.clicked.connect(lambda: handle_open_file(line_edit))

    working_days_label = QLabel("Number of Working Days:")
    working_days_edit = QLineEdit()

    calculate_button = QPushButton("Calculate B/D Time Percentage")
    calculate_button.clicked.connect(
        lambda: handle_calculate_bd_time_percentage(line_edit, working_days_edit, table_widget, plot_canvas))

    layout_1.addWidget(line_edit)
    layout_1.addWidget(open_button)
    layout_1.addWidget(working_days_label)
    layout_1.addWidget(working_days_edit)
    layout_1.addWidget(calculate_button)

    # Tab 2: View B/D Time Percentage in Table and Graph
    tab_2 = QWidget()
    layout_2 = QHBoxLayout(tab_2)

    table_widget = QTableWidget()
    table_widget.setColumnCount(3)
    table_widget.setHorizontalHeaderLabels(["Location", "% of B/D", "Target in %"])

    plot_canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
    layout_2.addWidget(table_widget)
    layout_2.addWidget(plot_canvas)

    tab_widget.addTab(tab_1, "Open Excel File")
    tab_widget.addTab(tab_2, "View B/D Time Percentage")

    main_window.setCentralWidget(tab_widget)
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
