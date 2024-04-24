import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog, QMessageBox, QLineEdit, QLabel, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def calculate_bd_time_percentage(file_path, working_days):
    # Read Excel file into a DataFrame
    df = pd.read_excel(file_path)

    area_line_map_table = {
        "SHOX": ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9", "DA-10", "DA-11", "VALVE ASSLY",
                 "SA-3", "SA-5", "WELDING"],
        "FFFA": ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF-1", "TFF-2"],
        "OT CELL": ["CELL-1", "CELL-2", "CELL-3", "CELL-4", "CELL-5", "CELL-6",
                    "CELL-7", "CELL-8", "CELL-9", "CELL-10", "CELL-11", "CELL-12"],
        "IT GRD": ["ITG-1", "ITG-2"]
    }

    time_availability = {
        "SHOX": {"DA-1": 880, "DA-2": 1260, "DA-3": 1260, "DA-4": 1260, "DA-5": 880,
                 "DA-7": 1260, "DA-9": 880, "DA-10": 880, "DA-11": 1260,
                 "VALVE ASSLY": 880, "SA-3": 1260, "SA-5": 440, "WELDING": 1260},
        "FFFA": {"FA-1": 1260, "FA-2": 1260, "FA-3": 1260, "FA-4": 1260,
                 "FA-5": 1260, "FA-6": 880, "FA-7": 440, "TFF-1": 1260, "TFF-2": 880},
        "OT CELL": {"CELL-1": 1260, "CELL-2": 1260, "CELL-3": 1260, "CELL-4": 1260,
                    "CELL-5": 1260, "CELL-6": 1260, "CELL-7": 1260, "CELL-8": 1260,
                    "CELL-9": 1260, "CELL-10": 1260, "CELL-11": 1260, "CELL-12": 1260},
        "IT GRD": {"ITG-1": 1260, "ITG-2": 880}
    }

    counts = {category: 0 for category in area_line_map_table}
    overall_plant_count = 0

    for _, row in df.iterrows():
        line = row[7]
        for category, keywords in area_line_map_table.items():
            if any(keyword in line for keyword in keywords):
                counts[category] += 1
                overall_plant_count += 1

    counts["Overall Plant"] = overall_plant_count

    print(f"counts\n{counts}")

    # Calculate sum of total time for each category
    sums = {}
    avail_time_sums = {}
    for category, keywords in area_line_map_table.items():
        total_sum = df[df["LINE"].isin(keywords)]["TOTAL TIME"].sum()
        sums[category] = total_sum
        avail_time_sum = sum(
            time_availability[category][keyword] for keyword in keywords if keyword in time_availability[category])
        avail_time_sums[category] = avail_time_sum

    print(f"sums\n{sums}")
    print(f"avail_time_sums\n{avail_time_sums}")

    # Calculate sum of total time for overall plant
    overall_plant_sum = sum(sums.values())
    overall_plant_avail_time_sum = sum(avail_time_sums.values())

    print(f"overall_plant_sum\n{overall_plant_sum}")
    print(f"overall_plant_avail_time_sum\n{overall_plant_avail_time_sum}")

    # Calculate B/D Time percentage for each category
    bd_time_percentages = {category: sums[category] / (avail_time_sums[category] * working_days) * 100 for category in
                           sums}
    overall_plant_bd_time_percentage = overall_plant_sum / (overall_plant_avail_time_sum * working_days) * 100

    print(f"bd_time_percentages\n{bd_time_percentages}")
    print(f"overall_plant_bd_time_percentage\n{overall_plant_bd_time_percentage}")

    # Display B/D Time percentages
    return bd_time_percentages, overall_plant_bd_time_percentage


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


def handle_calculate_bd_time_percentage(line_edit, working_days_edit, table_widget, plot_canvas):
    file_path = line_edit.text()
    if not file_path:
        QMessageBox.warning(None, 'No File Selected', 'No Excel file selected.')
        return

    working_days_str = working_days_edit.text()
    if not working_days_str.isdigit():
        QMessageBox.warning(None, 'Invalid Input', 'Please enter a valid number of working days.')
        return

    working_days = int(working_days_str)

    # Calculate B/D Time percentage
    bd_time_percentages, overall_plant_bd_time_percentage = calculate_bd_time_percentage(file_path, working_days)

    # Update table widget
    table_widget.setRowCount(len(bd_time_percentages) + 1)
    row = 0
    for category, percentage in bd_time_percentages.items():
        table_widget.setItem(row, 0, QTableWidgetItem(category))
        table_widget.setItem(row, 1, QTableWidgetItem(f"{percentage:.2f}%"))
        table_widget.setItem(row, 2, QTableWidgetItem("1%"))  # Target in %
        row += 1
    # Overall Plant row
    table_widget.setItem(row, 0, QTableWidgetItem("Overall Plant"))
    table_widget.setItem(row, 1, QTableWidgetItem(f"{overall_plant_bd_time_percentage:.2f}%"))
    table_widget.setItem(row, 2, QTableWidgetItem("1%"))  # Target in %

    # Plot graph
    categories = list(bd_time_percentages.keys()) + ["Overall Plant"]
    percentages = list(bd_time_percentages.values()) + [overall_plant_bd_time_percentage]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, percentages, color='skyblue')
    plt.xlabel('Location')
    plt.ylabel('% of B/D')
    plt.title('B/D Time Percentage')
    plt.xticks(rotation=45, ha='right')

    # Set y-axis range and draw red line at y = 1
    plt.ylim(0, 1.2)
    plt.axhline(y=1, color='red', linestyle='--')

    plot_canvas.figure = plt.gcf()
    plot_canvas.draw()


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
