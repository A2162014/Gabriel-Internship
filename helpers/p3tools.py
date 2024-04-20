import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTableWidgetItem, QWidget, QAbstractItemView, QTableWidget,
                             QHBoxLayout, QSizePolicy, QHeaderView, QSpacerItem)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from components.wpopup import *
from maps import area_line_map_statistics, time_availability


def add_widgets_to_scroll_area(scroll_area, table, df, num_working_days):
    # Create a widget to contain all the widgets vertically
    scroll_content_widget1 = QWidget()
    scroll_layout1 = QVBoxLayout(scroll_content_widget1)
    scroll_layout1.setAlignment(Qt.AlignCenter)

    # Create a widget to contain the existing table and graph side by side horizontally.
    widgets_widget1 = QWidget()
    widgets_layout1 = QHBoxLayout(widgets_widget1)
    widgets_layout1.setAlignment(Qt.AlignCenter)

    # Calculate the sum of total time for each category
    sums = {}
    avail_time_sums = {}
    for category, keywords in area_line_map_statistics.items():
        total_sum = df[df["LINE"].isin(keywords)]["TOTAL TIME"].sum()
        sums[category] = total_sum
        avail_time_sum = sum(
            time_availability[category][keyword] for keyword in keywords if keyword in time_availability[category])
        avail_time_sums[category] = avail_time_sum

    # Calculate the sum of total time for overall plant
    overall_plant_sum = sum(sums.values())
    overall_plant_avail_time_sum = sum(avail_time_sums.values())

    # Calculate B/D Time percentage for each category
    bd_time_percentages = {category: sums[category] / (avail_time_sums[category] * num_working_days) * 100
    if avail_time_sums[category] != 0 else 0 for category in sums}
    overall_plant_bd_time_percentage = overall_plant_sum / (overall_plant_avail_time_sum * num_working_days) * 100 \
        if overall_plant_avail_time_sum != 0 else 0

    # Add the existing table to the layout
    table_widget1 = QTableWidget(5, 3)  # 5 rows, 3 columns
    table_widget1.setHorizontalHeaderLabels(["Location", "% of B/D", "Target in %"])
    table_widget1.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget1.setFixedHeight(185)
    table_widget1.setFixedWidth(400)

    # Remove the outer box of the table
    table_widget1.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets = [1 for _ in range(5)]  # The Target is set to 1% for each row
    locations1 = ["Overall Plant"] + list(bd_time_percentages.keys())
    percentages1 = [overall_plant_bd_time_percentage] + list(bd_time_percentages.values())
    for i, (location1, percent1, target) in enumerate(zip(locations1, percentages1, targets)):
        item_location = QTableWidgetItem(location1)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget1.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{percent1:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget1.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget1.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget1.resizeRowsToContents()
    table_widget1.resizeColumnsToContents()
    table_widget1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout1.addWidget(table_widget1)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout1.addItem(spacer)

    # Add the existing graph to the layout
    fig, ax = plt.subplots()
    ax.bar(locations1, percentages1)
    ax.set_title('% of B/D')
    ax.axhline(y=1, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the y-axis limit to the maximum value plus 2
    max_value = max(percentages1) if percentages1 else 0
    ax.set_ylim([0, max_value + 1.25])

    # Display values above the bars
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2),
                ha='center', va='bottom')
    fig.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget1 = FigureCanvas(fig)
    bar_chart_widget1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout1.addWidget(bar_chart_widget1)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget1)

    # No. Of occurrences.
    widgets_widget7 = QWidget()
    widgets_layout7 = QHBoxLayout(widgets_widget7)
    widgets_layout7.setAlignment(Qt.AlignCenter)

    counts = {category: 0 for category in area_line_map_statistics}
    overall_plant_count = 0

    for i in range(table.rowCount()):
        item = table.item(i, 7)
        if item is not None:  # Check if the item exists
            line = item.text()
            for category, keywords in area_line_map_statistics.items():
                if any(keyword in line for keyword in keywords):
                    counts[category] += 1
                    overall_plant_count += 1

    counts["Overall Plant"] = overall_plant_count

    counts_ordered = {"Overall Plant": counts.pop("Overall Plant")}
    counts_ordered.update(counts)

    # Add the existing table to the layout
    table_widget2 = QTableWidget(5, 2)  # 5 rows, 3 columns
    table_widget2.setHorizontalHeaderLabels(["Location", "No of Occurrence"])
    table_widget2.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget2.setFixedHeight(185)
    table_widget2.setFixedWidth(400)

    # Remove the outer box of the table
    table_widget2.setStyleSheet("QTableWidget { border: none; }")

    for i, (locations2, occur) in enumerate(counts_ordered.items()):
        item_location = QTableWidgetItem(locations2)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to center
        table_widget2.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(str(occur))  # Convert to string
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to center
        table_widget2.setItem(i, 1, item_percent)

    # Enable word wrap
    table_widget2.resizeRowsToContents()
    table_widget2.resizeColumnsToContents()
    table_widget2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout7.addWidget(table_widget2)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget7)

    # MTBF in Day's
    widgets_widget2 = QWidget()
    widgets_layout2 = QHBoxLayout(widgets_widget2)

    # Calculate MTBF for each category
    mtbf = {}
    for category, total_sum in sums.items():
        # Calculate MTBF, handling division by zero (if count is zero)
        denominator = counts_ordered.get(category, 1)
        mtbf_val = (((avail_time_sums[category] * num_working_days) - total_sum) / denominator) / (60 * 24)
        mtbf[category] = mtbf_val if denominator != 0 else 0

    # Calculate MTBF for the overall plant, handling division by zero (if count is zero)
    overall_plant_denominator = counts_ordered.get("Overall Plant", 1)
    overall_plant_mtbf = (((sum(avail_time_sums.values()) * num_working_days) - sum(sums.values())) /
                          overall_plant_denominator) / (60 * 24)

    # Replace infinite values with 0
    overall_plant_mtbf = overall_plant_mtbf if overall_plant_denominator != 0 else 0

    # Add a new table below the existing widgets
    table_widget3 = QTableWidget(5, 3)  # 5 rows, 3 columns
    table_widget3.setHorizontalHeaderLabels(["Location", "MTBF", "Target in Day's"])
    table_widget3.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    table_widget3.setMinimumSize(402, 235)  # Set the fixed width and height for the table
    locations3 = ["Overall Plant"] + list(mtbf.keys())
    mtbf_values = [overall_plant_mtbf] + list(mtbf.values())
    targets2 = [1 for _ in range(5)]  # Example targets in days
    for i, (location3, mtbf, target2) in enumerate(zip(locations3, mtbf_values, targets2)):
        table_widget3.setItem(i, 0, QTableWidgetItem(location3))
        table_widget3.setItem(i, 1, QTableWidgetItem(f"{mtbf:.2f}"))
        table_widget3.setItem(i, 2, QTableWidgetItem(str(target2)))  # Set the target in days

    widgets_layout2.addWidget(table_widget3)

    # Add some spacing between the tables
    scroll_layout1.addSpacing(20)

    # Add bar chart for MTBF below the tables
    fig2, ax2 = plt.subplots()
    ax2.bar(locations3, mtbf_values)
    ax2.set_title('MTBF in Days')
    fig2.tight_layout()

    # Find the maximum value of mtbf_values
    max_mtbf_value = max(mtbf_values)

    # Set the y-axis limit with a gap of 100 above the maximum value
    ax2.set_ylim([0, max_mtbf_value + 100])

    # Draw a red line at y=1
    ax2.axhline(y=1, color='red', linestyle='-')

    # Add grid lines
    ax2.yaxis.grid(True)
    ax2.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Display values above the bars
    for bar2 in ax2.patches:
        ax2.text(bar2.get_x() + bar2.get_width() / 2, bar2.get_height() + 0.02, round(bar2.get_height(), 2),
                 ha='center', va='bottom')
    fig2.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget2 = FigureCanvas(fig2)
    bar_chart_widget2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    bar_chart_widget2.setMinimumSize(750, 325)  # Set the fixed width and height for the Matplotlib widget
    widgets_layout2.addWidget(bar_chart_widget2)

    scroll_layout1.addWidget(widgets_widget2)

    # MTTR in Mins
    widgets_widget3 = QWidget()
    widgets_layout3 = QHBoxLayout(widgets_widget3)

    # Add a new table below the existing widgets
    table_widget4 = QTableWidget(5, 3)  # 5 rows, 3 columns
    table_widget4.setHorizontalHeaderLabels(["Location", "MTTR", "Target in Min's"])
    table_widget4.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    table_widget4.setMinimumSize(402, 235)  # Set the fixed width and height for the table
    locations4 = ["Overall Plant", "Shox DA & FA", "FF FA", "OT Cell", "IT GRD"]
    mttr_values = [11.80, 12.60, 11.00, 12.50, 0]  # Example MTBF values
    targets3 = [30 for _ in range(5)]  # Example targets in days
    for i, (location4, mttr, target3) in enumerate(zip(locations4, mttr_values, targets3)):
        table_widget4.setItem(i, 0, QTableWidgetItem(location4))
        table_widget4.setItem(i, 1, QTableWidgetItem(str(mttr)))
        table_widget4.setItem(i, 2, QTableWidgetItem(str(target3)))  # Set the target in days

    widgets_layout3.addWidget(table_widget4)

    # Add some spacing between the tables
    scroll_layout1.addSpacing(20)

    # Add bar chart for MTBF below the tables
    fig3, ax3 = plt.subplots()
    ax3.bar(locations3, mttr_values)
    ax3.set_title('MTTR in Mins')
    fig3.tight_layout()

    # Set the y-axis limit to 160 days
    ax3.set_ylim([0, 35])

    # Draw a red line at y=1
    ax3.axhline(y=30, color='red', linestyle='-')

    # Add grid lines
    ax3.yaxis.grid(True)
    ax3.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Display values above the bars
    for bar3 in ax3.patches:
        ax3.text(bar3.get_x() + bar3.get_width() / 2, bar3.get_height() + 0.02, round(bar3.get_height(), 2),
                 ha='center', va='bottom')
    fig3.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget3 = FigureCanvas(fig3)
    bar_chart_widget3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    bar_chart_widget3.setMinimumSize(750, 325)  # Set the fixed width and height for the Matplotlib widget
    widgets_layout3.addWidget(bar_chart_widget3)

    scroll_layout1.addWidget(widgets_widget3)

    # SX Damper & FA
    widgets_widget4 = QWidget()
    widgets_layout4 = QHBoxLayout(widgets_widget4)

    # Add a new table below the existing widgets
    table_widget5 = QTableWidget(13, 3)  # 13 rows, 3 columns
    table_widget5.setHorizontalHeaderLabels(["Line", "% of B/D", "Target in %"])
    table_widget5.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    table_widget5.setMinimumSize(402, 400)  # Set the fixed width and height for the table
    lines1 = ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9",
              "DA-10", "DA-11", "Valve Assly", "SA-3", "SA-5", "Welding"]
    percentages2 = [0.26, 0.08, 0.09, 0.00, 0.00, 0.14, 0.11, 0.00, 0.27, 0.73, 0.00, 0.00, 0.00]  # Example MTBF values
    targets4 = [1 for _ in range(13)]  # Example targets in days
    for i, (line1, percent2, target4) in enumerate(zip(lines1, percentages2, targets4)):
        table_widget5.setItem(i, 0, QTableWidgetItem(line1))
        table_widget5.setItem(i, 1, QTableWidgetItem(str(percent2)))
        table_widget5.setItem(i, 2, QTableWidgetItem(str(target4)))  # Set the target in days

    widgets_layout4.addWidget(table_widget5)

    # Add some spacing between the tables
    scroll_layout1.addSpacing(20)

    # Add bar chart for MTBF below the tables
    fig4, ax4 = plt.subplots()
    ax4.bar(lines1, percentages2)
    ax4.set_title('SX Damper & FA')
    fig4.tight_layout()

    # Rotate the x-axis labels
    plt.xticks(rotation=45, ha='right')  # Rotate the labels by 45 degrees and align them to the right.

    # Set the y-axis limit to 160 days
    ax4.set_ylim([0, 35])

    # Draw a red line at y=1
    ax4.axhline(y=30, color='red', linestyle='-')

    # Add grid lines
    ax4.yaxis.grid(True)
    ax4.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Display values above the bars
    for bar4 in ax4.patches:
        ax4.text(bar4.get_x() + bar4.get_width() / 2, bar4.get_height() + 0.02, round(bar4.get_height(), 2),
                 ha='center', va='bottom')
    fig4.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget4 = FigureCanvas(fig4)
    bar_chart_widget4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    bar_chart_widget4.setMinimumSize(750, 325)  # Set the fixed width and height for the Matplotlib widget
    widgets_layout4.addWidget(bar_chart_widget4)

    scroll_layout1.addWidget(widgets_widget4)

    # Front Fork Final Assembly
    widgets_widget5 = QWidget()
    widgets_layout5 = QHBoxLayout(widgets_widget5)

    # Add a new table below the existing widgets
    table_widget6 = QTableWidget(9, 3)  # 13 rows, 3 columns
    table_widget6.setHorizontalHeaderLabels(["Line", "% of B/D", "Target in %"])
    table_widget6.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    table_widget6.setMinimumSize(402, 380)  # Set the fixed width and height for the table
    lines2 = ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF", "TFF-2"]
    percentages3 = [0.17, 0.43, 0.20, 0.06, 0.09, 0.26, 0.13, 0.06, 0.00]  # Example MTBF values
    targets5 = [1 for _ in range(9)]  # Example targets in days
    for i, (line2, percent3, target5) in enumerate(zip(lines2, percentages3, targets5)):
        table_widget6.setItem(i, 0, QTableWidgetItem(line2))
        table_widget6.setItem(i, 1, QTableWidgetItem(str(percent3)))
        table_widget6.setItem(i, 2, QTableWidgetItem(str(target5)))  # Set the target in days

    widgets_layout5.addWidget(table_widget6)

    # Add some spacing between the tables
    scroll_layout1.addSpacing(20)

    fig5, ax5 = plt.subplots()
    ax5.bar(lines2, percentages3)
    ax5.set_title('Front Fork Final Assembly')
    fig5.tight_layout()

    # Set the y-axis limit to 160 days
    ax5.set_ylim([0, 1.20])

    # Draw a red line at y=1
    ax5.axhline(y=1, color='red', linestyle='-')

    # Add grid lines
    ax5.yaxis.grid(True)
    ax5.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Display values above the bars
    for bar5 in ax5.patches:
        ax5.text(bar5.get_x() + bar5.get_width() / 2, bar5.get_height() + 0.02, round(bar5.get_height(), 2),
                 ha='center', va='bottom')
    fig5.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget5 = FigureCanvas(fig5)
    bar_chart_widget5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    bar_chart_widget5.setMinimumSize(750, 325)  # Set the fixed width and height for the Matplotlib widget
    widgets_layout5.addWidget(bar_chart_widget5)

    scroll_layout1.addWidget(widgets_widget5)

    # OT Cell & IT Grinding
    widgets_widget6 = QWidget()
    widgets_layout6 = QHBoxLayout(widgets_widget6)

    # Add a new table below the existing widgets
    table_widget7 = QTableWidget(14, 3)  # 13 rows, 3 columns
    table_widget7.setHorizontalHeaderLabels(["Line", "% of B/D", "Target in %"])
    table_widget7.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget7.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    table_widget7.setMinimumSize(402, 380)  # Set the fixed width and height for the table
    lines3 = ["Cell-1", "Cell-2", "Cell-3", "Cell-4", "Cell-5", "Cell-6", "Cell-7",
              "Cell-8", "Cell-9", "Cell-10", "Cell-11", "Cell-12", "ITG-1", "ITG-2"]
    percentages4 = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.05, 0.00, 0.00, 0.03, 0.00, 0.00, 0.00,
                    0.00]  # Example MTBF values
    targets6 = [1.50 for _ in range(14)]  # Example targets in days
    for i, (line3, percent4, target6) in enumerate(zip(lines3, percentages4, targets6)):
        table_widget7.setItem(i, 0, QTableWidgetItem(line3))
        table_widget7.setItem(i, 1, QTableWidgetItem(str(percent4)))
        table_widget7.setItem(i, 2, QTableWidgetItem(str(target6)))  # Set the target in days

    widgets_layout6.addWidget(table_widget7)

    # Add some spacing between the tables
    scroll_layout1.addSpacing(20)

    fig6, ax6 = plt.subplots()
    ax6.bar(lines3, percentages4)
    ax6.set_title('OT Cell & IT Grinding')
    fig6.tight_layout()

    # Rotate the x-axis labels
    plt.xticks(rotation=45, ha='right')  # Rotate the labels by 45 degrees and align them to the right.

    # Set the y-axis limit to 160 days
    ax6.set_ylim([0, 1.20])

    # Draw a red line at y=1
    ax6.axhline(y=1, color='red', linestyle='-')

    # Add grid lines
    ax6.yaxis.grid(True)
    ax6.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Display values above the bars
    for bar6 in ax6.patches:
        ax6.text(bar6.get_x() + bar6.get_width() / 2, bar6.get_height() + 0.02, round(bar6.get_height(), 2),
                 ha='center', va='bottom')
    fig6.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget6 = FigureCanvas(fig6)
    bar_chart_widget6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    bar_chart_widget6.setMinimumSize(750, 325)  # Set the fixed width and height for the Matplotlib widget
    widgets_layout6.addWidget(bar_chart_widget6)

    scroll_layout1.addWidget(widgets_widget6)

    # Set the widget containing all the widgets to the scroll area.
    scroll_area.setWidget(scroll_content_widget1)
