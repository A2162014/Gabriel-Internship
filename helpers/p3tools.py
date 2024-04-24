from maps import *
from components.wpopup import *

from math import floor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import (QTableWidgetItem, QWidget, QAbstractItemView, QTableWidget,
                             QHBoxLayout, QSizePolicy, QHeaderView, QSpacerItem, QFileDialog)


def get_area_for_line(line):
    for area, lines in area_line_map_table.items():
        if line in lines:
            return area
    return None


def save_statistics(scroll_area, tables, barcharts):
    # Get the directory and filename where the user wants to save the merged image
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Merged Image", "", "PNG (*.png)")
    if not file_path:
        return  # User canceled the dialog

    # Create the merged image with the exact height of the content
    merged_image = QPixmap(scroll_area.viewport().size().width(), 3300)
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


def add_widgets_to_scroll_area(scroll_area, file_name, df, num_working_days):
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
    for category, keywords in area_line_map_table.items():
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
    table_widget1.setHorizontalHeaderLabels(
        ["Location", f"% of B/D in {file_name.text().split('.')[0]}", "Target in %"])
    table_widget1.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget1.setFixedHeight(185)
    table_widget1.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget1.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets = [1 for _ in range(5)]  # The Target is set to 1% for each row
    locations1 = ["Overall Plant"] + area_stats_header
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
    ax.set_title(f"% of B/D in {file_name.text().split('.')[0]}")
    ax.axhline(y=1, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the y-axis limit to the maximum value plus 2
    max_value = max(percentages1) if percentages1 else 0
    ax.set_ylim([0, max_value + 1.20])

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
    widgets_widget2 = QWidget()
    widgets_layout2 = QHBoxLayout(widgets_widget2)
    widgets_layout2.setAlignment(Qt.AlignCenter)

    counts = {category: 0 for category in area_line_map_table}
    overall_plant_count = 0

    for index, row in df.iterrows():
        line = row["LINE"]  # Assuming the relevant column is always at index 7
        total_time = row["TOTAL TIME"]  # Assuming the column name for total time is "TOTAL TIME"
        if total_time > 0:
            for category, keywords in area_line_map_table.items():
                if any(keyword in line for keyword in keywords):
                    if line not in keywords:  # Check if the line is not in the list of keywords
                        continue  # Skip this line if it's not in the list of keywords
                    counts[category] += 1
                    overall_plant_count += 1

    counts["Overall Plant"] = overall_plant_count

    counts_ordered = {"Overall Plant": counts.pop("Overall Plant")}
    counts_ordered.update(counts)

    # Add the existing table to the layout
    table_widget2 = QTableWidget(5, 2)  # 5 rows, 3 columns
    table_widget2.setHorizontalHeaderLabels(["Location", f"No of Occurrence in {file_name.text().split('.')[0]}"])
    table_widget2.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget2.setFixedHeight(185)
    table_widget2.setFixedWidth(550)

    # Remove the outer box of the table
    table_widget2.setStyleSheet("QTableWidget { border: none; }")

    locations2 = ["Overall Plant"] + area_stats_header
    occurrences = list(counts_ordered.values())
    for i, (location2, occur) in enumerate(zip(locations2, occurrences)):
        item_location = QTableWidgetItem(location2)
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

    widgets_layout2.addWidget(table_widget2)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget2)

    # MTBF in Day's
    widgets_widget3 = QWidget()
    widgets_layout3 = QHBoxLayout(widgets_widget3)
    widgets_layout3.setAlignment(Qt.AlignCenter)

    # Calculate MTBF for each category
    mtbf = {}
    for category, total_sum in sums.items():
        # Calculate MTBF, handling division by zero (if count is zero)
        denominator = counts_ordered.get(category, 1)
        mtbf_val = (((avail_time_sums[category] * num_working_days) - total_sum) / denominator) / (
                60 * 24) if denominator != 0 else 0
        mtbf[category] = mtbf_val if denominator != 0 else 0

    # Calculate MTBF for the overall plant, handling division by zero (if count is zero)
    overall_plant_denominator = counts_ordered.get("Overall Plant", 1)
    overall_plant_mtbf = (((sum(avail_time_sums.values()) * num_working_days) - sum(sums.values())) /
                          overall_plant_denominator) / (60 * 24)

    # Replace infinite values with 0
    overall_plant_mtbf = overall_plant_mtbf if overall_plant_denominator != 0 else 0

    # Add the existing table to the layout
    table_widget3 = QTableWidget(5, 3)  # 5 rows, 3 columns
    table_widget3.setHorizontalHeaderLabels(
        ["Location", f"MTBF in {file_name.text().split('.')[0]}", "Target in Day's"])
    table_widget3.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget3.setFixedHeight(185)
    table_widget3.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget3.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets2 = [1 for _ in range(5)]  # The Target is set to 1% for each row
    locations3 = ["Overall Plant"] + area_stats_header
    mttr_values = [overall_plant_mtbf] + list(mtbf.values())
    for i, (location3, mttr, target2) in enumerate(zip(locations3, mttr_values, targets2)):
        item_location = QTableWidgetItem(location3)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget3.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{mttr:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget3.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target2))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget3.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget3.resizeRowsToContents()
    table_widget3.resizeColumnsToContents()
    table_widget3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout3.addWidget(table_widget3)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout3.addItem(spacer)

    # Add the existing graph to the layout
    fig2, ax2 = plt.subplots()
    ax2.bar(locations3, mttr_values)
    ax2.set_title(f"MTBF in Days - {file_name.text().split('.')[0]}")
    ax2.axhline(y=1, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax2.yaxis.grid(True)
    ax2.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the y-axis limit to the maximum value plus 2
    max_value2 = max(mttr_values) if mttr_values else 0
    ax2.set_ylim([0, floor(max_value2 + 30)])

    # Display values above the bars
    for bar2 in ax2.patches:
        ax2.text(bar2.get_x() + bar2.get_width() / 2, bar2.get_height(), round(bar2.get_height(), 2),
                 ha='center', va='bottom')
    fig2.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget2 = FigureCanvas(fig2)
    bar_chart_widget2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout3.addWidget(bar_chart_widget2)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget3)

    # MTTR in Mins
    widgets_widget4 = QWidget()
    widgets_layout4 = QHBoxLayout(widgets_widget4)
    widgets_layout4.setAlignment(Qt.AlignCenter)

    # Calculate MTTR for each category
    mttr = {}
    for category, total_sum in sums.items():
        if counts[category] != 0:
            mttr[category] = total_sum / counts[category]
        else:
            mttr[category] = 0

    # Calculate MTTR for overall plant
    overall_plant_mttr = sum(sums.values()) / overall_plant_count if overall_plant_count != 0 else 0

    # Add the existing table to the layout
    table_widget4 = QTableWidget(5, 3)  # 5 rows, 3 columns
    table_widget4.setHorizontalHeaderLabels(
        ["Location", f"MTTR in {file_name.text().split('.')[0]}", "TTarget in Min's"])
    table_widget4.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget4.setFixedHeight(185)
    table_widget4.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget4.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets3 = [30 for _ in range(5)]  # The Target is set to 1% for each row
    locations4 = ["Overall Plant"] + area_stats_header
    mtbf_values = [overall_plant_mttr] + list(mttr.values())
    for i, (location4, mtbf_val, target3) in enumerate(zip(locations4, mtbf_values, targets3)):
        item_location = QTableWidgetItem(location4)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget4.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{mtbf_val:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget4.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target3))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget4.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget4.resizeRowsToContents()
    table_widget4.resizeColumnsToContents()
    table_widget4.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout4.addWidget(table_widget4)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout4.addItem(spacer)

    # Add the existing graph to the layout
    fig3, ax3 = plt.subplots()
    ax3.bar(locations4, mtbf_values)
    ax3.set_title(f"MTTR in Mins - {file_name.text().split('.')[0]}")
    ax3.axhline(y=30, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax3.yaxis.grid(True)
    ax3.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the y-axis limit to the maximum value plus 2
    max_value3 = max(mtbf_values) if mtbf_values else 0
    ax3.set_ylim([0, floor(max_value3 + 35)])

    # Display values above the bars
    for bar3 in ax3.patches:
        ax3.text(bar3.get_x() + bar3.get_width() / 2, bar3.get_height(), round(bar3.get_height(), 2),
                 ha='center', va='bottom')
    fig3.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget3 = FigureCanvas(fig3)
    bar_chart_widget3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout4.addWidget(bar_chart_widget3)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget4)

    # SX Damper & FA
    widgets_widget5 = QWidget()
    widgets_layout5 = QHBoxLayout(widgets_widget5)
    widgets_layout5.setAlignment(Qt.AlignCenter)

    # Filter lines based on the location "SHOX"
    lines = area_line_map_table.get("SHOX", [])

    bd_percentages = {}
    for line in lines:
        df_line = df[df['LINE'].str.contains(line, case=False)]

        # Calculate sum of total time for line
        line_total_sum = df_line[df_line['LINE'] == line]["TOTAL TIME"].sum()

        # Get the availability time for the line
        area = get_area_for_line(line)
        line_avail_time = time_availability.get(area, {}).get(line, 0)

        # Calculate B/D Time percentage for line
        line_bd_time_percentage = (line_total_sum / (line_avail_time * num_working_days)) * 100
        bd_percentages[line] = line_bd_time_percentage

    # Add the existing table to the layout
    table_widget5 = QTableWidget(13, 3)  # 5 rows, 3 columns
    table_widget5.setHorizontalHeaderLabels(
        ["Line", f"% of B/D in {file_name.text().split('.')[0]}", "Target in %"])
    table_widget5.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget5.setFixedHeight(425)
    table_widget5.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget5.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets4 = [1 for _ in range(13)]  # The Target is set to 1% for each row
    line1_bd_percs = list(bd_percentages.values())
    for i, (line1_header, line1_bd_perc, target4) in enumerate(zip(lines1_stats_header, line1_bd_percs, targets4)):
        item_location = QTableWidgetItem(line1_header)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget5.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{line1_bd_perc:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget5.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target4))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget5.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget5.resizeRowsToContents()
    table_widget5.resizeColumnsToContents()
    table_widget5.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget5.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout5.addWidget(table_widget5)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout5.addItem(spacer)

    # Add the existing graph to the layout
    fig4, ax4 = plt.subplots()
    ax4.bar(lines1_stats_header, line1_bd_percs)
    ax4.set_title(f"SX Damper & FA - {file_name.text().split('.')[0]}")
    ax4.axhline(y=1, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax4.yaxis.grid(True)
    ax4.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the rotation angle for x-axis labels
    ax4.set_xticks(range(len(lines1_stats_header)))  # Set the positions of the ticks
    ax4.set_xticklabels(lines1_stats_header, rotation=45, ha='right')

    # Set the y-axis limit to the maximum value plus 2
    max_value4 = max(line1_bd_percs) if line1_bd_percs else 0
    ax4.set_ylim([0, max_value4 + 1.20])

    # Display values above the bars
    for bar4 in ax4.patches:
        ax4.text(bar4.get_x() + bar4.get_width() / 2, bar4.get_height(), round(bar4.get_height(), 2),
                 ha='center', va='bottom')
    fig4.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget4 = FigureCanvas(fig4)
    bar_chart_widget4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout5.addWidget(bar_chart_widget4)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget5)

    # Front Fork Final Assembly
    widgets_widget6 = QWidget()
    widgets_layout6 = QHBoxLayout(widgets_widget6)
    widgets_layout6.setAlignment(Qt.AlignCenter)

    # Filter lines based on the location "SHOX"
    lines1 = area_line_map_table.get("FFFA", [])

    bd_percentages1 = {}
    for line1 in lines1:
        df_line1 = df[df['LINE'].str.contains(line1, case=False)]

        # Calculate sum of total time for line
        line_total_sum1 = df_line1[df_line1['LINE'] == line1]["TOTAL TIME"].sum()

        # Get the availability time for the line
        area1 = get_area_for_line(line1)
        line_avail_time1 = time_availability.get(area1, {}).get(line1, 0)

        # Calculate B/D Time percentage for line
        line_bd_time_percentage1 = (line_total_sum1 / (line_avail_time1 * num_working_days)) * 100
        bd_percentages1[line1] = line_bd_time_percentage1

    # Add the existing table to the layout
    table_widget6 = QTableWidget(9, 3)  # 5 rows, 3 columns
    table_widget6.setHorizontalHeaderLabels(
        ["Line", f"% of B/D in {file_name.text().split('.')[0]}", "Target in %"])
    table_widget6.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget6.setFixedHeight(310)
    table_widget6.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget6.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets5 = [1 for _ in range(13)]  # The Target is set to 1% for each row
    line2_bd_percs = list(bd_percentages1.values())
    for i, (line2_header, line2_bd_perc, target5) in enumerate(zip(lines2_stats_header, line2_bd_percs, targets5)):
        item_location = QTableWidgetItem(line2_header)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget6.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{line2_bd_perc:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget6.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target5))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget6.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget6.resizeRowsToContents()
    table_widget6.resizeColumnsToContents()
    table_widget6.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget6.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout6.addWidget(table_widget6)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout6.addItem(spacer)

    # Add the existing graph to the layout
    fig5, ax5 = plt.subplots()
    ax5.bar(lines2_stats_header, line2_bd_percs)
    ax5.set_title(f"Front Fork Final Assembly - {file_name.text().split('.')[0]}")
    ax5.axhline(y=1, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax5.yaxis.grid(True)
    ax5.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the rotation angle for x-axis labels
    ax5.set_xticks(range(len(lines2_stats_header)))  # Set the positions of the ticks
    ax5.set_xticklabels(lines2_stats_header, rotation=45, ha='right')

    # Set the y-axis limit to the maximum value plus 2
    max_value5 = max(line2_bd_percs) if line2_bd_percs else 0
    ax5.set_ylim([0, max_value5 + 1.20])

    # Display values above the bars
    for bar5 in ax5.patches:
        ax5.text(bar5.get_x() + bar5.get_width() / 2, bar5.get_height(), round(bar5.get_height(), 2),
                 ha='center', va='bottom')
    fig5.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget5 = FigureCanvas(fig5)
    bar_chart_widget5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout6.addWidget(bar_chart_widget5)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget6)

    # OT cell & IT Grinding
    widgets_widget7 = QWidget()
    widgets_layout7 = QHBoxLayout(widgets_widget7)
    widgets_layout7.setAlignment(Qt.AlignCenter)

    # Filter lines based on the locations "OT CELL" and "IT GRD"
    lines2 = []
    for location in ["OT CELL", "IT GRD"]:
        lines2.extend(area_line_map_table.get(location, []))
    print(f"lines {lines2}")

    bd_percentages2 = {}
    for line2 in lines2:
        df_line2 = df[df['LINE'].str.contains(line2, case=False)]
        print(f"df_line {df_line2}")

        # Calculate sum of total time for line
        line_total_sum2 = df_line2[df_line2['LINE'] == line2]["TOTAL TIME"].sum()
        print(f"line_total_sum {line_total_sum2}")

        # Get the availability time for the line
        area2 = get_area_for_line(line2)
        line_avail_time2 = time_availability.get(area2, {}).get(line2, 0)
        print(f"line_avail_time {line_avail_time2}")

        # Calculate B/D Time percentage for line
        line_bd_time_percentage2 = (line_total_sum2 / (line_avail_time2 * num_working_days)) * 100
        bd_percentages2[line2] = line_bd_time_percentage2

    # Add the existing table to the layout
    table_widget7 = QTableWidget(14, 3)  # 5 rows, 3 columns
    table_widget7.setHorizontalHeaderLabels(
        ["Line", f"% of B/D in {file_name.text().split('.')[0]}", "Target in %"])
    table_widget7.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table non-editable
    table_widget7.setFixedHeight(460)
    table_widget7.setFixedWidth(600)

    # Remove the outer box of the table
    table_widget7.setStyleSheet('''
        QTableWidget { 
            border: none; 
        }
    ''')

    targets6 = [1.50 for _ in range(14)]  # The Target is set to 1% for each row
    line34_bd_percs = list(bd_percentages2.values())
    for i, (line34_header, line34_bd_perc, target6) in enumerate(zip(lines34_stats_header, line34_bd_percs, targets6)):
        item_location = QTableWidgetItem(line34_header)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_location.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget7.setItem(i, 0, item_location)

        item_percent = QTableWidgetItem(f"{line34_bd_perc:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_percent.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget7.setItem(i, 1, item_percent)

        item_target = QTableWidgetItem(str(target6))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make the item selectable and enabled
        item_target.setTextAlignment(Qt.AlignCenter)  # Align text to top-left
        table_widget7.setItem(i, 2, item_target)

    # Enable word wrap
    table_widget7.resizeRowsToContents()
    table_widget7.resizeColumnsToContents()
    table_widget7.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Allow horizontal stretching
    table_widget7.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar

    widgets_layout7.addWidget(table_widget7)

    spacer = QSpacerItem(60, 20)  # width, height
    widgets_layout7.addItem(spacer)

    # Add the existing graph to the layout
    fig6, ax6 = plt.subplots()
    ax6.bar(lines34_stats_header, line34_bd_percs)
    ax6.set_title(f"OT Cell & IT Grinding - {file_name.text().split('.')[0]}")
    ax6.axhline(y=1.5, color='r', linestyle='-')  # Add a red-dashed line at y=1%
    ax6.yaxis.grid(True)
    ax6.xaxis.grid(False)  # Hide the grid lines along the x-axis

    # Set the rotation angle for x-axis labels
    ax6.set_xticks(range(len(lines34_stats_header)))  # Set the positions of the ticks
    ax6.set_xticklabels(lines34_stats_header, rotation=45, ha='right')

    # Set the y-axis limit to the maximum value plus 2
    max_value6 = max(line34_bd_percs) if line34_bd_percs else 0
    ax6.set_ylim([0, max_value6 + 1.7])

    # Display values above the bars
    for bar6 in ax6.patches:
        ax6.text(bar6.get_x() + bar6.get_width() / 2, bar6.get_height(), round(bar6.get_height(), 2),
                 ha='center', va='bottom')
    fig6.tight_layout()

    # Embed the Matplotlib figure in a QWidget
    bar_chart_widget6 = FigureCanvas(fig6)
    bar_chart_widget6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set vertical policy to Fixed
    widgets_layout7.addWidget(bar_chart_widget6)

    # Add the existing widgets to the scroll layout
    scroll_layout1.addWidget(widgets_widget7)

    # Set the scroll area's widget to the content widget
    scroll_area.setWidget(scroll_content_widget1)

    # Add the existing tables to the 'tables' list
    tables.extend(
        [table_widget1, table_widget2, table_widget3, table_widget4, table_widget5, table_widget6, table_widget7])

    # Add the existing bar charts to the 'barcharts' list
    barcharts.extend([bar_chart_widget1, bar_chart_widget2, bar_chart_widget3,
                      bar_chart_widget4, bar_chart_widget5, bar_chart_widget6])
