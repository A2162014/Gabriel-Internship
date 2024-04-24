import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog, QMessageBox, QLineEdit, QLabel, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def calculate_mttr(file_path):
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

    counts = {category: 0 for category in categories}
    overall_plant_count = 0

    for _, row in df.iterrows():
        line = row[7]
        for category, keywords in categories.items():
            if any(keyword in line for keyword in keywords):
                counts[category] += 1
                overall_plant_count += 1

    counts["Overall Plant"] = overall_plant_count

    # Calculate sum of total time for each category
    sums = {}
    for category, keywords in categories.items():
        total_sum = df[df["LINE"].isin(keywords)]["TOTAL TIME"].sum()
        sums[category] = total_sum

    # Calculate MTTR for each category
    mttr = {}
    for category, total_sum in sums.items():
        if counts[category] != 0:
            mttr[category] = total_sum / counts[category]
        else:
            mttr[category] = 0

    # Calculate MTTR for overall plant
    overall_plant_mttr = sum(sums.values()) / overall_plant_count if overall_plant_count != 0 else 0

    return mttr, overall_plant_mttr


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

    # Calculate MTTR
    mttr, overall_plant_mttr = calculate_mttr(file_path)

    # Update table widget
    table_widget.setRowCount(len(mttr) + 1)
    row = 0
    for category, value in mttr.items():
        table_widget.setItem(row, 0, QTableWidgetItem(category))
        table_widget.setItem(row, 1, QTableWidgetItem(f"{value:.2f}"))
        table_widget.setItem(row, 2, QTableWidgetItem(""))  # Target in %
        row += 1
    # Overall Plant row
    table_widget.setItem(row, 0, QTableWidgetItem("Overall Plant"))
    table_widget.setItem(row, 1, QTableWidgetItem(f"{overall_plant_mttr:.2f}"))
    table_widget.setItem(row, 2, QTableWidgetItem(""))  # Target in %

    # Plot graph (not applicable for MTTR)

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
