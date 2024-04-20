import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QFileDialog, QTabWidget
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, categories):
        super().__init__()

        self.categories = categories

        self.setWindowTitle("Count Occurrences Example")
        self.setup_ui()

    def setup_ui(self):
        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.table_tab = QWidget()
        self.occurrences_tab = QWidget()

        # Setup table tab
        self.setup_table_tab()

        # Setup occurrences tab
        self.setup_occurrences_tab()

        # Add tabs to tab widget
        self.tab_widget.addTab(self.table_tab, "View Table")
        self.tab_widget.addTab(self.occurrences_tab, "View Occurrences")

        self.setCentralWidget(self.tab_widget)

    def setup_table_tab(self):
        table_layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        table_layout.addWidget(self.table_widget)
        self.table_tab.setLayout(table_layout)

    def setup_occurrences_tab(self):
        occurrences_layout = QVBoxLayout()
        self.occurrences_table_widget = QTableWidget()
        occurrences_layout.addWidget(self.occurrences_table_widget)
        self.occurrences_tab.setLayout(occurrences_layout)

    def populate_table_from_excel(self, filename):
        try:
            df = pd.read_excel(filename)
            df = df.where(pd.notnull(df), '')  # Replace NaN values with empty strings
            data = df.values.tolist()
            headers = df.columns.tolist()

            self.table_widget.setRowCount(len(data))
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)

            for row, rowData in enumerate(data):
                for col, val in enumerate(rowData):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(val)))
        except Exception as e:
            print(f"Error loading Excel file: {e}")

    def count_occurrences(self):
        counts = {category: 0 for category in self.categories}
        overall_plant_count = 0

        for row in range(self.table_widget.rowCount()):
            line = self.table_widget.item(row, 7).text()
            for category, keywords in self.categories.items():
                if any(keyword in line for keyword in keywords):
                    counts[category] += 1
                    overall_plant_count += 1

        counts["Overall Plant"] = overall_plant_count

        return counts

    def display_occurrences(self, occurrences):
        # Move "Overall Plant" to the beginning of the dictionary
        occurrences_ordered = {"Overall Plant": occurrences.pop("Overall Plant")}
        occurrences_ordered.update(occurrences)

        self.occurrences_table_widget.setRowCount(len(occurrences_ordered))
        self.occurrences_table_widget.setColumnCount(2)
        self.occurrences_table_widget.setHorizontalHeaderLabels(["Category", "Occurrences"])

        for row, (category, count) in enumerate(occurrences_ordered.items()):
            self.occurrences_table_widget.setItem(row, 0, QTableWidgetItem(category))
            self.occurrences_table_widget.setItem(row, 1, QTableWidgetItem(str(count)))

    def open_excel_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if filename:
            self.populate_table_from_excel(filename)
            occurrences = self.count_occurrences()
            self.display_occurrences(occurrences)

def main():
    app = QApplication(sys.argv)

    categories = {
        "Shox DA & FA": ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9", "DA-10", "DA-11", "Valve Assly", "SA-3", "SA-5", "Welding"],
        "FF FA": ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF-1", "TFF-2"],
        "OT Cell": ["Cell-1", "Cell-2", "Cell-3", "Cell-4", "Cell-5", "Cell-6", "Cell-7", "Cell-8", "Cell-9", "Cell-10", "Cell-11", "Cell-12"],
        "IT GRD": ["ITG-1", "ITG-2"]
    }

    main_window = MainWindow(categories)
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
