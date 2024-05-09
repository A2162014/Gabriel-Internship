import json
import os
from math import floor

import numpy as np
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QHBoxLayout, QFileDialog, QHeaderView, QSizePolicy,
                             QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox)
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from components.titledTable import TitledTableWidget
from helpers import tab1Utils
from helpers.maps import (connect_to_database, fetch_values, fetch_lonames_for_ano, current_dir, create_full_map,
                          create_time_availability_machines, create_time_availability_lines, month_map, stat_headers,
                          tables, barcharts, extract_lines_machines_problems_of_area)

table_widget = None
bar_chart_widget = None
container_widget = None
line_edits = None
current_month = 0


def scroll_to_top(tab3_scroll_area):
    tab3_scroll_area.verticalScrollBar().setValue(0)


def load_line_edit_values(json_file_path):
    try:
        with open(json_file_path) as f:
            data = json.load(f)
            return data.get('line_edits')
    except FileNotFoundError:
        show_error_message("JSON file not found.")
        return None
    except json.JSONDecodeError:
        show_error_message("Error decoding JSON file.")
        return None


def save_statistics(scroll_area):
    if not tables and not barcharts:
        QMessageBox.warning(None, "Cannot Save", "Please select statistics to save.")
        return
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Merged Image", "", "PNG (*.png)")
    if not file_path:
        return
    for table_widget in tables:
        if table_widget is not None:
            table_widget.clearSelection()
    merged_image_height = scroll_area.viewport().size().height()
    merged_image = QPixmap(scroll_area.viewport().size().width(), merged_image_height)
    merged_image.fill(Qt.white)
    painter = QPainter(merged_image)
    painter.begin(merged_image)
    y_offset = 0
    for table_widget in tables:
        if table_widget is not None:
            table_pixmap = QPixmap(table_widget.size())
            table_widget.render(table_pixmap)
            table_pos = table_widget.mapTo(scroll_area.viewport(), QPoint(0, 0))
            painter.drawPixmap(table_pos, table_pixmap)
            y_offset += table_widget.height()
    if barcharts is not None:
        for bar_chart_widget in barcharts:
            if bar_chart_widget is not None:
                bar_chart_pixmap = QPixmap(bar_chart_widget.size())
                bar_chart_widget.render(bar_chart_pixmap)
                bar_chart_pos = bar_chart_widget.mapTo(scroll_area.viewport(), QPoint(0, 0))
                painter.drawPixmap(bar_chart_pos, bar_chart_pixmap)
                y_offset += bar_chart_widget.height()
    painter.end()
    merged_image.save(file_path)
    has_horizontal_scrollbar = scroll_area.horizontalScrollBar().isVisible()
    has_vertical_scrollbar = scroll_area.verticalScrollBar().isVisible()
    is_horizontal_at_end = scroll_area.horizontalScrollBar().value() == scroll_area.horizontalScrollBar().maximum()
    is_vertical_at_end = scroll_area.verticalScrollBar().value() == scroll_area.verticalScrollBar().maximum()
    if has_horizontal_scrollbar and has_vertical_scrollbar:
        message_text = "Please scroll vertically and horizontally to view the full statistics."
    elif has_horizontal_scrollbar:
        if not is_horizontal_at_end:
            message_text = "Please scroll horizontally to view the full statistics."
        else:
            return
    elif has_vertical_scrollbar:
        if not is_vertical_at_end:
            message_text = "Please scroll vertically to view the full statistics."
        else:
            return
    else:
        return
    message_box = QMessageBox()
    message_box.setWindowTitle("Scroll to View Full Statistics")
    message_box.setIcon(QMessageBox.Information)
    message_box.setText(message_text)
    message_box.exec_()


def show_error_message(message, parent=None):
    error_dialog = QMessageBox(parent)
    error_dialog.warning(parent, "Error", f'<span style="font-size: 12pt;">{message}</span>')


def get_area_for_line(line):
    with connect_to_database() as conn:
        area_line_map, _, _, _ = create_full_map(conn)
    for area, lines in area_line_map.items():
        if line in lines:
            return area
    return None


def get_area_for_machine(machine):
    with connect_to_database() as conn:
        area_line_map, line_machine_map, _, _ = create_full_map(conn)
    for area, lines in area_line_map.items():
        for line in lines:
            if machine in line_machine_map.get(line, []):
                return area
    return None


def get_line_edit(month, line_edits):
    return line_edits[month - 1] if 1 <= month <= 12 else None  # Ensure month is within valid range


def calculate_bd(area_line_map, dataframe, line_edits, month, time_availability):
    sums = {}
    avail_time_sums = {}
    for category, keywords in area_line_map.items():
        total_sum = dataframe[(dataframe["LINE"].isin(keywords)) & (dataframe["MONTH"] == month)]["TOTAL TIME"].sum()
        sums[category] = total_sum
        avail_time_sum = sum(
            time_availability[category][keyword] for keyword in keywords if keyword in time_availability[category])
        avail_time_sums[category] = avail_time_sum
    num_rows_locations = len(avail_time_sums) + 1
    overall_plant_sum = sum(sums.values())
    overall_plant_avail_time_sum = sum(avail_time_sums.values())
    num_days = get_line_edit(month, line_edits)
    print(month)
    print(num_days)
    bd_time_percentages = {category: sums[category] / (avail_time_sums[category] * num_days) * 100
    if avail_time_sums[category] != 0 else 0 for category in sums}
    overall_plant_bd_time_percentage = overall_plant_sum / (overall_plant_avail_time_sum * num_days) * 100 \
        if overall_plant_avail_time_sum != 0 else 0
    return num_rows_locations, sums, total_sum, avail_time_sums, bd_time_percentages, overall_plant_bd_time_percentage


def calculate_occurrences_locations(area_line_map, dataframe, month):
    counts = {category: 0 for category in area_line_map}
    overall_plant_count = 0
    for index, row in dataframe[dataframe["MONTH"] == month].iterrows():
        line = row["LINE"]
        total_time = row["TOTAL TIME"]
        if total_time > 0:
            for category, keywords in area_line_map.items():
                if any(keyword in line for keyword in keywords):
                    if line not in keywords:
                        continue
                    counts[category] += 1
                    overall_plant_count += 1
    counts["Overall Plant"] = overall_plant_count
    counts_ordered = {"Overall Plant": counts.pop("Overall Plant")}
    counts_ordered.update(counts)
    return counts, counts_ordered, overall_plant_count


def get_key(month_map, value):
    for key, val in month_map.items():
        if val == value:
            return key
    return None


def get_bd_locations(month, area_line_map, dataframe, time_availability, line_edits, area_stats_header):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    num_rows_locations, _, _, _, bd_time_percentages, overall_plant_bd_time_percentage = calculate_bd(area_line_map,
                                                                                                      dataframe,
                                                                                                      line_edits,
                                                                                                      month,
                                                                                                      time_availability)
    table_widget = QTableWidget(num_rows_locations, 3)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"% of B/D in {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(
        ["Location", f"% of B/D", "Target in %"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_widget.setFixedHeight(48 * num_rows_locations)
    table_widget.setFixedWidth(600)
    table_widget.setStyleSheet('''
        QTableWidget {
            border: none;
        }
    ''')
    targets = [line_edits[12] for _ in range(num_rows_locations)]
    locations = ["Overall Plant"] + area_stats_header
    percentages = [overall_plant_bd_time_percentage] + list(bd_time_percentages.values())
    for i, (location, percent, target) in enumerate(zip(locations, percentages, targets)):
        item_location = QTableWidgetItem(location)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_location.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_location)
        item_percent = QTableWidgetItem(f"{percent:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_percent)
        item_target = QTableWidgetItem(str(target))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_target.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_target)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    spacer = QSpacerItem(60, 20)
    widget_layout.addItem(spacer)
    fig, ax = plt.subplots()
    ax.bar(locations, percentages)
    ax.set_title(f"% of B/D in {month_title}")
    ax.axhline(y=float(line_edits[12]), color='r', linestyle='-')
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    max_value = max(percentages) if percentages else 0
    ax.set_ylim([0, max_value + (float(line_edits[12]) + 0.2)])
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2),
                ha='center', va='bottom')
    fig.tight_layout()
    plt.close(fig)
    bar_chart_widget = FigureCanvas(fig)
    bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    widget_layout.addWidget(bar_chart_widget)
    return table_widget, bar_chart_widget, container_widget


def get_occurrences_locations(month, area_line_map, dataframe, line_edits, time_availability, area_stats_header):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    num_rows_locations, _, _, _, _, _ = calculate_bd(area_line_map, dataframe, line_edits, month, time_availability)
    _, counts_ordered, _ = calculate_occurrences_locations(area_line_map, dataframe, month)
    table_widget = QTableWidget(num_rows_locations, 2)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"No of Occurrence in {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(["Location", f"No of Occurrence"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_widget.setFixedHeight(48 * num_rows_locations)
    table_widget.setFixedWidth(550)
    table_widget.setStyleSheet("QTableWidget { border: none; }")
    locations = ["Overall Plant"] + area_stats_header
    occurrences = list(counts_ordered.values())
    for i, (location, occur) in enumerate(zip(locations, occurrences)):
        item_location = QTableWidgetItem(location)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_location.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_location)
        item_percent = QTableWidgetItem(str(occur))
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_percent)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    return table_widget, container_widget


def get_occurrences_machines_problems(lines_machines_problems, dataframe, required_area, month):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    problem_to_machines = {}
    machine_to_line = {}
    for line, machine, problem in lines_machines_problems:
        if problem not in problem_to_machines:
            problem_to_machines[problem] = set()
        problem_to_machines[problem].add(machine)
        machine_to_line[machine] = line
    counts = {problem: 0 for problem in problem_to_machines.keys()}
    for index, row in dataframe[dataframe["MONTH"] == month].iterrows():
        total_time = row["TOTAL TIME"]
        if total_time > 0:
            area = row["AREA"]
            if area == required_area:
                machine = row["MACHINE"]
                problem = row["PROBLEM"]
                if problem in counts:
                    counts[problem] += 1
    sorted_counts = {k: v for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True)}
    table_widget = QTableWidget(len(sorted_counts), 4)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"No of Occurrence in {required_area} - {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(["Line", "Machine", "Problem", f"No of Occurrence"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    if len(sorted_counts) < 5:
        table_widget.setFixedHeight(75 * len(sorted_counts))
    elif len(sorted_counts) < 30:
        table_widget.setFixedHeight(51 * len(sorted_counts))
    elif len(sorted_counts) < 40:
        table_widget.setFixedHeight(56 * len(sorted_counts))
    else:
        table_widget.setFixedHeight(35 * len(sorted_counts))
    table_widget.setFixedWidth(1400)
    table_widget.setStyleSheet("QTableWidget { border: none; }")
    problems = list(sorted_counts.keys())
    occurrences = list(sorted_counts.values())
    for i, problem in enumerate(problems):
        machines = ', '.join(problem_to_machines[problem])
        lines = ', '.join(set(machine_to_line[machine] for machine in problem_to_machines[problem]))
        item_lines = QTableWidgetItem(lines)
        item_lines.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_lines.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_lines)
        item_machines = QTableWidgetItem(machines)
        item_machines.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_machines.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_machines)
        item_problem = QTableWidgetItem(problem)
        item_problem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_problem.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_problem)
        item_occurrence = QTableWidgetItem(str(occurrences[i]))
        item_occurrence.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_occurrence.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 3, item_occurrence)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    return table_widget, container_widget


def get_mtbf_locations(month, area_line_map, dataframe, time_availability, line_edits, area_stats_header):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    _, counts_ordered, _ = calculate_occurrences_locations(area_line_map, dataframe, month)
    num_rows_locations, sums, _, avail_time_sums, _, _ = calculate_bd(area_line_map, dataframe, line_edits, month,
                                                                      time_availability)
    mtbf = {}
    num_days = get_line_edit(month, line_edits)
    for category, total_sum in sums.items():
        denominator = counts_ordered.get(category, 1)
        mtbf_val = (((avail_time_sums[category] * num_days) - total_sum) / denominator) / (
                60 * 24) if denominator != 0 else 0
        mtbf[category] = mtbf_val if denominator != 0 else 0
    overall_plant_denominator = counts_ordered.get("Overall Plant", 1)
    overall_plant_mtbf = (((sum(avail_time_sums.values()) * num_days) - sum(sums.values())) /
                          overall_plant_denominator) / (60 * 24)
    overall_plant_mtbf = overall_plant_mtbf if overall_plant_denominator != 0 else 0
    table_widget = QTableWidget(num_rows_locations, 3)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"MTBF - {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(
        ["Location", f"MTBF in Days", "Target in Day's"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_widget.setFixedHeight(48 * num_rows_locations)
    table_widget.setFixedWidth(600)
    table_widget.setStyleSheet('''
        QTableWidget {
            border: none;
        }
    ''')
    targets = [line_edits[13] for _ in range(num_rows_locations)]
    locations = ["Overall Plant"] + area_stats_header
    mttr_values = [overall_plant_mtbf] + list(mtbf.values())
    for i, (location, mttr, target) in enumerate(zip(locations, mttr_values, targets)):
        item_location = QTableWidgetItem(location)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_location.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_location)
        item_percent = QTableWidgetItem(f"{mttr:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_percent)
        item_target = QTableWidgetItem(str(target))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_target.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_target)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    spacer = QSpacerItem(60, 20)
    widget_layout.addItem(spacer)
    fig, ax = plt.subplots()
    ax.bar(locations, mttr_values)
    ax.set_title(f"MTBF in Days - {month_title}")
    ax.axhline(y=float(line_edits[13]), color='r', linestyle='-')
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    max_value = max(mttr_values) if mttr_values else 0
    ax.set_ylim([0, floor(max_value + 30)])
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2),
                ha='center', va='bottom')
    fig.tight_layout()
    plt.close(fig)
    bar_chart_widget = FigureCanvas(fig)
    bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    widget_layout.addWidget(bar_chart_widget)
    return table_widget, bar_chart_widget, container_widget


def get_mttr_locations(month, area_line_map, dataframe, time_availability, line_edits, area_stats_header):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    counts, _, overall_plant_count = calculate_occurrences_locations(area_line_map, dataframe, month)
    num_rows_locations, sums, _, _, _, time_availability_lines = calculate_bd(area_line_map, dataframe, line_edits,
                                                                              month, time_availability)
    mttr = {}
    for category, total_sum in sums.items():
        if counts[category] != 0:
            mttr[category] = total_sum / counts[category]
        else:
            mttr[category] = 0
    overall_plant_mttr = sum(sums.values()) / overall_plant_count if overall_plant_count != 0 else 0
    table_widget = QTableWidget(num_rows_locations, 3)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"MTTR - {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(
        ["Location", f"MTTR in Mins", "Target in Min's"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_widget.setFixedHeight(48 * num_rows_locations)
    table_widget.setFixedWidth(600)
    table_widget.setStyleSheet('''
        QTableWidget {
            border: none;
        }
    ''')
    targets = [line_edits[14] for _ in range(num_rows_locations)]
    locations = ["Overall Plant"] + area_stats_header
    mtbf_values = [overall_plant_mttr] + list(mttr.values())
    for i, (location, mtbf_val, target) in enumerate(zip(locations, mtbf_values, targets)):
        item_location = QTableWidgetItem(location)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_location.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_location)
        item_percent = QTableWidgetItem(f"{mtbf_val:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_percent)
        item_target = QTableWidgetItem(str(target))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_target.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_target)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    spacer = QSpacerItem(60, 20)
    widget_layout.addItem(spacer)
    fig, ax = plt.subplots()
    ax.bar(locations, mtbf_values)
    ax.set_title(f"MTTR in Mins - {month_title}")
    ax.axhline(y=float(line_edits[14]), color='r', linestyle='-')
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    max_value = max(mtbf_values) if mtbf_values else 0
    ax.set_ylim([0, floor(max_value + (float(line_edits[14]) + 5))])
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2),
                ha='center', va='bottom')
    fig.tight_layout()
    plt.close(fig)
    bar_chart_widget = FigureCanvas(fig)
    bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    widget_layout.addWidget(bar_chart_widget)
    return table_widget, bar_chart_widget, container_widget


def get_bd_lines(month, area_line_map, required_area, dataframe, time_availability,
                 line_edits, lines_stats_header, required_header):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    bd_percentages = {}
    if required_area == ["OT CELL", "IT GRD"]:
        lines = []
        for location in required_area:
            lines.extend(area_line_map.get(location, []))
    else:
        lines = area_line_map.get(required_area, [])
    for line in lines:
        df_line = dataframe[(dataframe['LINE'].str.contains(line, case=False)) & (dataframe["MONTH"] == month)]
        line_total_sum = df_line[df_line['LINE'] == line]["TOTAL TIME"].sum()
        area = get_area_for_line(line)
        line_avail_time = time_availability.get(area, {}).get(line, 0)
        num_days = get_line_edit(month, line_edits)
        line_bd_time_percentage = (line_total_sum / (line_avail_time * num_days)) * 100
        bd_percentages[line] = line_bd_time_percentage
    table_widget = QTableWidget(len(lines_stats_header), 3)
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"% of B/D in {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(
        ["Line", f"% of B/D", "Target in %"])
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table_widget.setFixedHeight(36 * (len(lines_stats_header) + 1))
    table_widget.setFixedWidth(600)
    table_widget.setStyleSheet('''
        QTableWidget {
            border: none;
        }
    ''')
    if required_area == "SHOX":
        targets = [line_edits[15] for _ in range(len(lines_stats_header))]
    elif required_area == "FFFA":
        targets = [line_edits[16] for _ in range(len(lines_stats_header))]
    else:
        targets = [line_edits[17] for _ in range(len(lines_stats_header))]
    line_bd_percs = list(bd_percentages.values())
    for i, (line_header, line_bd_perc, target4) in enumerate(zip(lines_stats_header, line_bd_percs, targets)):
        item_location = QTableWidgetItem(line_header)
        item_location.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_location.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_location)
        item_percent = QTableWidgetItem(f"{line_bd_perc:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_percent)
        item_target = QTableWidgetItem(str(target4))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_target.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_target)
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    spacer = QSpacerItem(60, 20)
    widget_layout.addItem(spacer)
    fig, ax = plt.subplots()
    ax.bar(lines_stats_header, line_bd_percs)
    ax.set_title(f"{required_header} - {month_title}")
    if required_area == "SHOX":
        ax.axhline(y=float(line_edits[15]), color='r', linestyle='-')
    elif required_area == "FFFA":
        ax.axhline(y=float(line_edits[16]), color='r', linestyle='-')
    else:
        ax.axhline(y=float(line_edits[17]), color='r', linestyle='-')
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    ax.set_xticks(range(len(lines_stats_header)))
    ax.set_xticklabels(lines_stats_header, rotation=45, ha='right')
    max_value = max(line_bd_percs) if line_bd_percs else 0
    if required_area == "SHOX":
        ax.set_ylim([0, max_value + (float(line_edits[15]) + 0.2)])
    elif required_area == "FFFA":
        ax.set_ylim([0, max_value + (float(line_edits[16]) + 0.2)])
    else:
        ax.set_ylim([0, max_value + (float(line_edits[17]) + 0.2)])
    ax.set_ylim([0, max_value + (float(line_edits[16]) + 0.2)])
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2),
                ha='center', va='bottom')
    fig.tight_layout()
    plt.close(fig)
    bar_chart_widget = FigureCanvas(fig)
    bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    widget_layout.addWidget(bar_chart_widget)
    return table_widget, bar_chart_widget, container_widget


def get_bd_machines(month, dataframe, time_availability_machines, line_edits, required_header,
                    lines_machines_problems, required_areas=None):
    container_widget = QWidget()
    widget_layout = QHBoxLayout(container_widget)
    widget_layout.setAlignment(Qt.AlignCenter)
    machines = {}
    bd_percentages = {}
    num_days = get_line_edit(month, line_edits)
    if required_areas == ["OT CELL", "IT GRD"]:
        for area in required_areas:
            with connect_to_database() as conn:
                machines_and_problems = extract_lines_machines_problems_of_area(conn, area)
                for line, machine, problem in machines_and_problems:
                    df_machine = dataframe[(dataframe['MACHINE'] == machine) & (dataframe["MONTH"] == month)]
                    machine_total_sum = df_machine["TOTAL TIME"].sum()
                    area = get_area_for_machine(machine)
                    machine_avail_time = time_availability_machines.get(area, {}).get(machine, 0)
                    if machine_avail_time * num_days != 0:
                        machine_bd_time_percentage = (machine_total_sum / (machine_avail_time * num_days)) * 100
                        bd_percentages[machine] = machine_bd_time_percentage
                    else:
                        bd_percentages[machine] = np.nan
                    if machine in machines:
                        if line not in machines[machine]:  # Ensure unique lines for each machine
                            machines[machine].append(line)
                    else:
                        machines[machine] = [line]
        sorted_machines = sorted(machines.keys(), key=lambda x: bd_percentages.get(x, 0), reverse=True)
    else:
        for line, machine, problem in lines_machines_problems:
            df_machine = dataframe[(dataframe['MACHINE'] == machine) & (dataframe["MONTH"] == month)]
            machine_total_sum = df_machine["TOTAL TIME"].sum()
            area = get_area_for_machine(machine)
            machine_avail_time = time_availability_machines.get(area, {}).get(machine, 0)
            if machine_avail_time * num_days != 0:
                machine_bd_time_percentage = (machine_total_sum / (machine_avail_time * num_days)) * 100
                bd_percentages[machine] = machine_bd_time_percentage
            else:
                bd_percentages[machine] = np.nan
            if machine in machines:
                if line not in machines[machine]:  # Ensure unique lines for each machine
                    machines[machine].append(line)
            else:
                machines[machine] = [line]
        sorted_machines = sorted(machines.keys(), key=lambda x: bd_percentages[x], reverse=True)
    table_widget = QTableWidget(len(sorted_machines), 4)  # Added one more column for Line
    month_title = get_key(month_map, month)
    table_widget = TitledTableWidget(f"% of B/D in {month_title}", table_widget)
    table_widget.setHorizontalHeaderLabels(
        ["Lines", "Machine", f"% of B/D", "Target in %"])  # Added "Lines" header
    table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    if len(sorted_machines) < 5:
        table_widget.setFixedHeight(73 * len(sorted_machines))
    elif len(sorted_machines) < 25:
        table_widget.setFixedHeight(43 * len(sorted_machines))
    else:
        table_widget.setFixedHeight(35 * len(sorted_machines))
    table_widget.setFixedWidth(1250)
    table_widget.setStyleSheet('''
        QTableWidget {
            border: none;
        }
    ''')
    if required_header == "SX Damper & FA":
        targets = [line_edits[18] for _ in range(len(sorted_machines))]
    elif required_header == "Front Fork Final Assembly":
        targets = [line_edits[19] for _ in range(len(sorted_machines))]
    else:
        targets = [line_edits[20] for _ in range(len(sorted_machines))]
    machine_bd_percs = [bd_percentages[machine] for machine in sorted_machines]  # Extracting machine from tuple
    for i, (machine, machine_bd_perc, target) in enumerate(zip(sorted_machines, machine_bd_percs, targets)):
        unique_lines = ", ".join(sorted(machines[machine]))  # Sort lines for consistency
        item_lines = QTableWidgetItem(unique_lines)
        item_lines.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_lines.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 0, item_lines)  # Set item for Lines
        item_machine = QTableWidgetItem(machine)
        item_machine.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_machine.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 1, item_machine)  # Changed column index for machine
        item_percent = QTableWidgetItem(f"{machine_bd_perc:.2f}")
        item_percent.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_percent.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 2, item_percent)  # Changed column index for % of B/D
        item_target = QTableWidgetItem(str(target))
        item_target.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_target.setTextAlignment(Qt.AlignCenter)
        table_widget.setItem(i, 3, item_target)  # Changed column index for Target
    table_widget.resizeRowsToContents()
    table_widget.resizeColumnsToContents()
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget_layout.addWidget(table_widget)
    machine_bd_percs_filtered = [val for val in machine_bd_percs if not np.isnan(val) and not np.isinf(val)]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(list(reversed(sorted_machines)), list(reversed(machine_bd_percs)))  # Using labels with both machine and unique lines
    ax.set_title(f"{required_header} - {month_title}")
    if required_header == "SX Damper & FA":
        ax.axvline(x=float(line_edits[18]), color='r', linestyle='-')
    elif required_header == "Front Fork Final Assembly":
        ax.axvline(x=float(line_edits[19]), color='r', linestyle='-')
    else:
        ax.axvline(x=float(line_edits[20]), color='r', linestyle='-')
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    ax.set_yticks(range(len(sorted_machines)))
    ax.set_yticklabels(list(reversed(sorted_machines)))  # Using labels with both machine and unique lines
    if required_header == "SX Damper & FA":
        if machine_bd_percs_filtered:
            max_value = max(machine_bd_percs_filtered)
            ax.set_xlim([0, max_value + (float(line_edits[18]) + 0.2)])
        else:
            ax.set_xlim([0, float(line_edits[18]) + 1])
    elif required_header == "Front Fork Final Assembly":
        if machine_bd_percs_filtered:
            max_value = max(machine_bd_percs_filtered)
            ax.set_xlim([0, max_value + (float(line_edits[19]) + 0.2)])
        else:
            ax.set_xlim([0, float(line_edits[19]) + 1])
    else:
        if machine_bd_percs_filtered:
            max_value = max(machine_bd_percs_filtered)
            ax.set_xlim([0, max_value + (float(line_edits[20]) + 0.2)])
        else:
            ax.set_xlim([0, float(line_edits[20]) + 1])
    for bar in ax.patches:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, round(bar.get_width(), 2),
                va='center', ha='left')
    fig.tight_layout()
    plt.close(fig)
    bar_chart_widget = FigureCanvas(fig)
    bar_chart_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    widget_layout.addWidget(bar_chart_widget)
    return table_widget, bar_chart_widget, container_widget


def display_statistics(tree_widget_left, scroll_area):
    global table_widget, bar_chart_widget, container_widget, line_edits, current_month
    del tables[:]
    del barcharts[:]
    df = tab1Utils.df
    json_file_path = os.path.join(os.path.dirname(current_dir), 'statistic_values.json')
    if json_file_path:
        line_edits_from_json = load_line_edit_values(json_file_path)
        if line_edits_from_json:
            line_edits = line_edits_from_json
    with connect_to_database() as conn:
        area_stats_header = fetch_values(conn, "SELECT AONAME FROM AREA")
        lines1_stats_header = fetch_lonames_for_ano(conn, 1)
        lines2_stats_header = fetch_lonames_for_ano(conn, 2)
        lines34_stats_header = fetch_lonames_for_ano(conn, 3) + fetch_lonames_for_ano(conn, 4)
        area_line_map, line_machine_map, machine_problem_map, problem_caction_map = create_full_map(conn)
        time_availability_lines = create_time_availability_lines(conn)
        time_availability_machines = create_time_availability_machines(conn)
        lines_machines_problems_shox = extract_lines_machines_problems_of_area(conn, 'SHOX')
        lines_machines_problems_fffa = extract_lines_machines_problems_of_area(conn, 'FFFA')
        lines_machines_problems_otcell = extract_lines_machines_problems_of_area(conn, 'OT CELL')
        lines_machines_problems_itgrd = extract_lines_machines_problems_of_area(conn, 'IT GRD')
        conn.commit()
    scroll_content_widget = QWidget()
    scroll_layout = QVBoxLayout(scroll_content_widget)
    scroll_layout.setAlignment(Qt.AlignCenter)
    selected_items = tree_widget_left.selectedItems()
    if not selected_items:
        tree_widget_left.setToolTip("")
        scrollAreaContent = scroll_area.takeWidget()
        if scrollAreaContent:
            scrollAreaContent.deleteLater()
        return
    else:
        tooltip_text = "\n".join(item.text(0) for item in selected_items)
        tree_widget_left.setToolTip(tooltip_text)

    for item in selected_items:
        parent_item = item.parent()
        if parent_item:
            parent_text = parent_item.text(0)
            if parent_text in month_map.keys():
                current_month = month_map[parent_text]
                child_text = item.text(0)
                if child_text in stat_headers:
                    if current_month not in df["MONTH"].values:
                        current_month = 0
                        return
                    if (child_text == stat_headers[1] or child_text == stat_headers[2]
                            or child_text == stat_headers[3] or child_text == stat_headers[4]
                            or child_text == stat_headers[4]):
                        table_widget, _, container_widget = run_function(current_month, child_text, df,
                                                                         line_edits, area_stats_header,
                                                                         lines1_stats_header,
                                                                         lines2_stats_header,
                                                                         lines34_stats_header, area_line_map,
                                                                         time_availability_lines,
                                                                         time_availability_machines,
                                                                         lines_machines_problems_shox,
                                                                         lines_machines_problems_fffa,
                                                                         lines_machines_problems_otcell,
                                                                         lines_machines_problems_itgrd)
                        tables.append(table_widget)
                    else:
                        table_widget, bar_chart_widget, container_widget = run_function(current_month, child_text, df,
                                                                                        line_edits, area_stats_header,
                                                                                        lines1_stats_header,
                                                                                        lines2_stats_header,
                                                                                        lines34_stats_header,
                                                                                        area_line_map,
                                                                                        time_availability_lines,
                                                                                        time_availability_machines,
                                                                                        lines_machines_problems_shox,
                                                                                        lines_machines_problems_fffa,
                                                                                        lines_machines_problems_otcell,
                                                                                        lines_machines_problems_itgrd)

                        tables.append(table_widget)
                        barcharts.append(bar_chart_widget)
                    scroll_layout.addWidget(container_widget)
                    scroll_area.setWidget(scroll_content_widget)


def run_function(month, stat_header, dataframe, line_edits, area_stats_header, lines1_stats_header,
                 lines2_stats_header, lines34_stats_header, area_line_map, time_availability_lines,
                 time_availability_machines, lines_machines_problems_shox, lines_machines_problems_fffa,
                 lines_machines_problems_otcell, lines_machines_problems_itgrd):
    global table_widget, bar_chart_widget, container_widget
    if stat_header == stat_headers[0]:
        table_widget, bar_chart_widget, container_widget = get_bd_locations(month, area_line_map, dataframe,
                                                                            time_availability_lines, line_edits,
                                                                            area_stats_header)
    elif stat_header == stat_headers[1]:
        table_widget, container_widget = get_occurrences_locations(month, area_line_map, dataframe, line_edits,
                                                                   time_availability_lines, area_stats_header)
    elif stat_header == stat_headers[2]:
        table_widget, container_widget = get_occurrences_machines_problems(lines_machines_problems_shox, dataframe,
                                                                           "SHOX", month)
    elif stat_header == stat_headers[3]:
        table_widget, container_widget = get_occurrences_machines_problems(lines_machines_problems_fffa, dataframe,
                                                                           "FFFA", month)
    elif stat_header == stat_headers[4]:
        table_widget, container_widget = get_occurrences_machines_problems(lines_machines_problems_otcell, dataframe,
                                                                           "OT CELL", month)
    elif stat_header == stat_headers[5]:
        table_widget, container_widget = get_occurrences_machines_problems(lines_machines_problems_itgrd, dataframe,
                                                                           "IT GRD", month)
    elif stat_header == stat_headers[6]:
        table_widget, bar_chart_widget, container_widget = get_mtbf_locations(month, area_line_map, dataframe,
                                                                              time_availability_lines, line_edits,
                                                                              area_stats_header)
    elif stat_header == stat_headers[7]:
        table_widget, bar_chart_widget, container_widget = get_mttr_locations(month, area_line_map, dataframe,
                                                                              time_availability_lines, line_edits,
                                                                              area_stats_header)
    elif stat_header == stat_headers[8]:
        table_widget, bar_chart_widget, container_widget = get_bd_lines(month, area_line_map, "SHOX", dataframe,
                                                                        time_availability_lines, line_edits,
                                                                        lines1_stats_header, "SX Damper & FA")
    elif stat_header == stat_headers[9]:
        table_widget, bar_chart_widget, container_widget = get_bd_lines(month, area_line_map, "FFFA", dataframe,
                                                                        time_availability_lines, line_edits,
                                                                        lines2_stats_header,
                                                                        "Front Fork Final Assembly")
    elif stat_header == stat_headers[10]:
        table_widget, bar_chart_widget, container_widget = get_bd_lines(month, area_line_map,
                                                                        ["OT CELL", "IT GRD"], dataframe,
                                                                        time_availability_lines, line_edits,
                                                                        lines34_stats_header, "OT Cell & IT Grinding")
    elif stat_header == stat_headers[11]:
        table_widget, bar_chart_widget, container_widget = get_bd_machines(month, dataframe, time_availability_machines,
                                                                           line_edits, "SX Damper & FA",
                                                                           lines_machines_problems_shox)
    elif stat_header == stat_headers[12]:
        table_widget, bar_chart_widget, container_widget = get_bd_machines(month, dataframe, time_availability_machines,
                                                                           line_edits, "Front Fork Final Assembly",
                                                                           lines_machines_problems_fffa)
    elif stat_header == stat_headers[13]:
        table_widget, bar_chart_widget, container_widget = get_bd_machines(month, dataframe, time_availability_machines,
                                                                           line_edits, "OT Cell & IT Grinding",
                                                                           lines_machines_problems_shox,
                                                                           ["OT CELL", "IT GRD"])

    return table_widget, bar_chart_widget, container_widget
