import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import os
import zipfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, \
    QLabel, QSizePolicy, QScrollArea, QHBoxLayout, QGroupBox, QPushButton, QFileDialog, QLineEdit
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class ScrollAreaExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Scroll Area Example")
        self.setGeometry(100, 100, 800, 500)  # Increased window height

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        # Create a layout for the scroll area content
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Add groups of table and graph side by side
        self.table_widgets = []
        self.graph_widgets = []
        for i in range(3):
            # Create a horizontal layout for each group
            group_layout = QHBoxLayout()

            # Create a group box to contain the table
            table_group_box = QGroupBox("Table {}".format(i + 1))
            table_layout = QVBoxLayout()

            # Create a table widget
            table_widget = QTableWidget(5, 3)
            table_widget.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])
            table_widget.setFixedWidth(400)  # Set fixed width
            table_widget.setFixedHeight(225)  # Set fixed height
            for row in range(5):
                for col in range(3):
                    item = QTableWidgetItem(str(random.randint(1, 100)))
                    table_widget.setItem(row, col, item)
            table_layout.addWidget(table_widget)
            table_group_box.setLayout(table_layout)

            # Create a group box to contain the graph
            graph_group_box = QGroupBox("Graph {}".format(i + 1))
            graph_layout = QVBoxLayout()

            # Generate sample data for the graph
            x = np.linspace(0, 10, 100)
            y = np.sin(x) + np.random.normal(0, 0.1, 100)

            # Create a figure and plot the data
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_xlabel("X-axis")
            ax.set_ylabel("Y-axis")
            canvas = FigureCanvasQTAgg(fig)
            canvas.setFixedSize(400, 225)  # Set fixed size for canvas
            graph_layout.addWidget(canvas)
            graph_group_box.setLayout(graph_layout)

            # Add the table and graph group boxes to the horizontal layout
            group_layout.addWidget(table_group_box)
            group_layout.addWidget(graph_group_box)

            # Add the horizontal layout to the scroll layout
            self.scroll_layout.addLayout(group_layout)

            # Keep references to table and graph widgets
            self.table_widgets.append(table_widget)
            self.graph_widgets.append(fig)

        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)

        # Add a save button below the scroll area
        save_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        save_layout.addWidget(self.save_button)

        # Add line edit for file name
        self.file_name_edit = QLineEdit()
        self.file_name_edit.setPlaceholderText("Enter file name")
        save_layout.addWidget(self.file_name_edit)

        layout.addLayout(save_layout)

        # Show the main window
        self.show()

    def save_data(self):
        file_name = self.file_name_edit.text()
        if not file_name:
            print("Please enter a file name.")
            return

        # Open a dialog to select the directory
        save_path = QFileDialog.getExistingDirectory(self, "Select Directory")

        if save_path:
            # Create a directory to store images
            images_dir = os.path.join(save_path, "images")
            os.makedirs(images_dir, exist_ok=True)

            # Save images of tables
            for i, table_widget in enumerate(self.table_widgets):
                screenshot = table_widget.grab()
                screenshot.save(os.path.join(images_dir, f"table_{i + 1}.png"), "png")

            # Save images of graphs
            for i, fig in enumerate(self.graph_widgets):
                fig.savefig(os.path.join(images_dir, f"graph_{i + 1}.png"))

            # Zip the images
            with zipfile.ZipFile(os.path.join(save_path, f"{file_name}.zip"), "w") as zipf:
                for root, dirs, files in os.walk(images_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), images_dir))

            print("Images saved and zipped successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScrollAreaExample()
    sys.exit(app.exec_())
