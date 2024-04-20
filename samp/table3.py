import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog, QMessageBox, QLineEdit, QLabel, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def calculate_mtbf(file_path, working_days):
    # Read Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Define categories
    categories = {
        "Shox DA & FA": ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9", "DA-10", "DA-11", "Valve Assly",
                         "SA-3", "SA-5", "Welding"],
        "FF FA": ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF-1", "TFF-2"],
        "OT Cell": ["CELL-1", "CELL-2", "CELL-3", "CELL-4", "CELL-5", "CELL-6", "CELL-7", "CELL-8", "CELL-9", "CELL-10",
                    "CELL-11", "CELL-12"],
        "IT GR": ["ITG-1", "ITG-2"]
    }

    # Define time availability for each category
    time_availability = {
        "Shox DA & FA": {"DA-1": 880, "DA-2": 1260, "DA-3": 1260, "DA-4": 1260, "DA-5": 880, "DA-7": 1260, "DA-9": 880,
                         "DA-10": 880, "DA-11": 1260, "Valve Assly": 880, "SA-3": 1260, "SA-5": 440, "Welding": 1260},
        "FF FA": {"FA-1": 1260, "FA-2": 1260, "FA-3": 1260, "FA-4": 1260, "FA-5": 1260, "FA-6": 880, "FA-7": 440,
                  "TFF-1": 1260, "TFF-2": 880},
        "OT Cell": {"CELL-1": 1260, "CELL-2": 1260, "CELL-3": 1260, "CELL-4": 1260, "CELL-5": 1260, "CELL-6": 1260,
                    "CELL-7": 1260, "CELL-8": 1260, "CELL-9": 1260, "CELL-10": 1260, "CELL-11": 1260, "CELL-12": 1260},
        "IT GR": {"ITG-1": 1260, "ITG-2": 880}
    }

    counts = {category: 0 for category in categories}
    overall_plant_count = 0

    for _, row in df.iterrows():
        line = row[7]
        for category, keywords in categories.items():
            if any(keyword in line for keyword in keywords):
                counts[category] += 1
                overall_plant_count += 1

    counts["Overall Plant"] = overall_plant_count

    print(f"counts\n{counts}")

    # Calculate sum of total time for each category
    sums = {}
    avail_time_sums = {}
    for category, keywords in categories.items():
        total_sum = df[df["LINE"].isin(keywords)]["TOTAL TIME"].sum()
        sums[category] = total_sum
        avail_time_sum = sum(
            time_availability[category][keyword] for keyword in keywords if keyword in time_availability[category])
        avail_time_sums[category] = avail_time_sum

    print(f"sums\n{sums}")
    print(f"avail_time_sums\n{avail_time_sums}")

    # Calculate MTBF for each category
    mtbf = {}
    for category, total_sum in sums.items():
        mtbf[category] = (((avail_time_sums[category] * working_days) - total_sum) / counts[category]) / (60 * 24)

    # Calculate MTBF for overall plant
    overall_plant_mtbf = (((sum(avail_time_sums.values()) * working_days) - sum(sums.values())) /
                          counts["Overall Plant"]) / (60 * 24)

    print(f"mtbf\n{mtbf}")
    print(f"overall_plant_mtbf\n{overall_plant_mtbf}")

    return mtbf, overall_plant_mtbf


def open_file_dialog():
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(None, "Open Excel File", "", "Excel Files (*.xls *.xlsx)",
                                               options=options)
    if file_name:
        return file_name
    else:
        return None


def handle_open_file(line_edit):
    file_path = open_file_dialog()
    if file_path:
        line_edit.clear()
        line_edit.setText(file_path)
    else:
        QMessageBox.warning(None, 'No File Selected', 'No Excel file selected.')


def handle_calculate_mtbf(line_edit, working_days_edit, table_widget, plot_canvas):
    file_path = line_edit.text()
    if not file_path:
        QMessageBox.warning(None, 'No File Selected', 'No Excel file selected.')
        return

    working_days_str = working_days_edit.text()
    if not working_days_str.isdigit():
        QMessageBox.warning(None, 'Invalid Input', 'Please enter a valid number of working days.')
        return

    working_days = int(working_days_str)

    # Calculate MTBF
    mtbf, overall_plant_mtbf = calculate_mtbf(file_path, working_days)

    # Update table widget
    table_widget.setRowCount(len(mtbf) + 1)
    row = 0
    for category, value in mtbf.items():
        table_widget.setItem(row, 0, QTableWidgetItem(category))
        table_widget.setItem(row, 1, QTableWidgetItem(f"{value:.2f}"))
        table_widget.setItem(row, 2, QTableWidgetItem(""))  # Target in %
        row += 1
    # Overall Plant row
    table_widget.setItem(row, 0, QTableWidgetItem("Overall Plant"))
    table_widget.setItem(row, 1, QTableWidgetItem(f"{overall_plant_mtbf:.2f}"))
    table_widget.setItem(row, 2, QTableWidgetItem(""))  # Target in %

    # Plot graph (not applicable for MTBF)

    # Clear the canvas
    plot_canvas.figure.clear()
    plot_canvas.draw()


def main():
    app = QApplication([])

    main_window = QMainWindow()
    main_window.setWindowTitle("Excel MTBF Calculator")

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

    calculate_button = QPushButton("Calculate MTBF")
    calculate_button.clicked.connect(
        lambda: handle_calculate_mtbf(line_edit, working_days_edit, table_widget, plot_canvas))

    layout_1.addWidget(line_edit)
    layout_1.addWidget(open_button)
    layout_1.addWidget(working_days_label)
    layout_1.addWidget(working_days_edit)
    layout_1.addWidget(calculate_button)

    # Tab 2: View MTBF in Table
    tab_2 = QWidget()
    layout_2 = QHBoxLayout(tab_2)

    table_widget = QTableWidget()
    table_widget.setColumnCount(3)
    table_widget.setHorizontalHeaderLabels(["Location", "MTBF (days)", "Target in %"])

    plot_canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
    layout_2.addWidget(table_widget)
    layout_2.addWidget(plot_canvas)

    tab_widget.addTab(tab_1, "Open Excel File")
    tab_widget.addTab(tab_2, "View MTBF")

    main_window.setCentralWidget(tab_widget)
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
