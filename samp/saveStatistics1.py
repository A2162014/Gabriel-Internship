import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QSizePolicy, QScrollArea, QHBoxLayout, QFileDialog


class ScrollableApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tables and Bar Charts')
        self.setGeometry(100, 100, 800, 600)

        # Create a QVBoxLayout
        layout = QVBoxLayout()

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a widget to hold the content of the scroll area
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)

        # Add tables and bar charts to the scroll area
        self.tables = []
        self.barcharts = []
        for i in range(5):
            table_widget = self.createTable()
            table_widget.setFixedSize(400, 200)  # Set the size here
            self.tables.append(table_widget)
            bar_chart_widget = self.createBarChart()
            bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.barcharts.append(bar_chart_widget)

            # Create a QHBoxLayout for each row
            row_layout = QHBoxLayout()
            row_layout.addWidget(table_widget)
            row_layout.addWidget(bar_chart_widget)

            scroll_content_layout.addLayout(row_layout)

        # Set the scroll content widget
        self.scroll_area.setWidget(scroll_content)

        layout.addWidget(self.scroll_area)

        # Create a QPushButton for saving
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda: saveData(self.scroll_area, self.tables, self.barcharts))
        layout.addWidget(save_button)

        # Set the layout
        self.setLayout(layout)

    def createTable(self):
        table_widget = QTableWidget()
        table_widget.setColumnCount(3)
        table_widget.setRowCount(5)

        for i in range(5):
            for j in range(3):
                item = QTableWidgetItem(f'Row {i}, Col {j}')
                table_widget.setItem(i, j, item)

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()

        return table_widget

    def createBarChart(self):
        fig, ax = plt.subplots()
        x = np.arange(5)
        y = np.random.randint(1, 10, size=5)
        ax.bar(x, y)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_title('Bar Chart')

        # Create a canvas
        canvas = FigureCanvas(fig)

        return canvas


def saveData(scroll_area, tables, barcharts):
    # Get the directory and filename where the user wants to save the merged image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Merged Image", "", "PNG (*.png)")
    if not file_path:
        return  # User canceled the dialog

    # Create the merged image with the exact height of the content
    merged_image = QPixmap(scroll_area.viewport().size().width(), 2450)
    merged_image.fill(Qt.white)  # Fill the pixmap with white background

    painter = QPainter(merged_image)
    painter.begin(merged_image)

    # Initialize the y-coordinate for drawing content
    y_offset = 0

    # Draw tables onto the merged image
    for table_widget in tables:
        table_pixmap = QPixmap(table_widget.size())
        table_widget.render(table_pixmap)
        table_pos = table_widget.mapTo(scroll_area.viewport(), QPoint(0, 0))
        painter.drawPixmap(table_pos, table_pixmap)
        y_offset += table_widget.height()

    # Draw bar charts onto the merged image
    for bar_chart_widget in barcharts:
        bar_chart_pixmap = QPixmap(bar_chart_widget.size())
        bar_chart_widget.render(bar_chart_pixmap)
        bar_chart_pos = bar_chart_widget.mapTo(scroll_area.viewport(), QPoint(0, 0))
        painter.drawPixmap(bar_chart_pos, bar_chart_pixmap)
        y_offset += bar_chart_widget.height()

    painter.end()

    # Save the merged image
    merged_image.save(file_path)
    print("Image saved successfully.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScrollableApp()
    window.showMaximized()  # Open the window maximized
    sys.exit(app.exec_())
