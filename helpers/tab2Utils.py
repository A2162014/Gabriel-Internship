import sqlite3

from PyQt5 import QtCore

from components.suggestionBar import CompleterDelegate
from helpers.maps import connect_to_database, fetch_area_line_data_tab2, create_full_map

from materials.styles import treeStyle
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem


def set_labels(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
               line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
               corrective_action_line_edit, area_name, line_name, result, *args):
    if result:
        area_name_db, line_name_db, tavail = result
        area_value_line_edit_short.setText(area_name)
        area_value_line_edit_full.setText(area_name_db)
        line_value_line_edit_short.setText(line_name)
        line_value_line_edit_full.setText(line_name_db)
        time_value_line_edit.setText(str(tavail))
        if args:
            machine_line_edit.setText(args[0])
            if len(args) > 1:
                problem_line_edit.setText(args[1])
                if len(args) > 2:
                    corrective_action_line_edit.setText(args[2])


def update_labels(item, area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                  line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                  corrective_action_line_edit):
    if item is None:
        return
    parent_items = []
    current_item = item
    while current_item.parent() is not None:
        parent_text = current_item.parent().text(0)
        if parent_text != "Overall Plant":
            parent_items.append(parent_text)
        current_item = current_item.parent()
    if not parent_items:
        return
    with connect_to_database() as conn:
        try:
            if len(parent_items) == 1:
                result = fetch_area_line_data_tab2(conn, parent_items[0], item.text(0))
                set_labels(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                           line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                           corrective_action_line_edit, parent_items[0], item.text(0), result)
                machine_line_edit.clear()
                problem_line_edit.clear()
                corrective_action_line_edit.clear()
            elif len(parent_items) == 2:
                result = fetch_area_line_data_tab2(conn, parent_items[1], parent_items[0])
                set_labels(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                           line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                           corrective_action_line_edit, parent_items[1], parent_items[0], result,
                           item.text(0))
                problem_line_edit.clear()
                corrective_action_line_edit.clear()
            elif len(parent_items) == 3:
                result = fetch_area_line_data_tab2(conn, parent_items[2], parent_items[1])
                set_labels(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                           line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                           corrective_action_line_edit, parent_items[2], parent_items[1], result,
                           parent_items[0], item.text(0))
                corrective_action_line_edit.clear()
            elif len(parent_items) == 4:
                result = fetch_area_line_data_tab2(conn, parent_items[3], parent_items[2])
                set_labels(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                           line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                           corrective_action_line_edit, parent_items[3], parent_items[2], result,
                           parent_items[1], parent_items[0], item.text(0))
        except Exception as e:
            print("An error occurred:", e)


def update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                       line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                       machine_line_edit, problem_line_edit, corrective_action_line_edit):
    # Store expanded state before updating
    expanded_states = {}
    for item in tree_widget.findItems("", QtCore.Qt.MatchContains):
        expanded_states[item.text(0)] = item.isExpanded()

    with connect_to_database() as conn:
        tree_widget.clear()
        area_line_map, line_machine_map, machine_problem_map, problem_caction_map = create_full_map(conn)
        tree_widget.setStyleSheet(treeStyle)
        tree_widget.setHeaderHidden(True)
        for area, lines in area_line_map.items():
            area_item = QTreeWidgetItem([area])
            for line in lines:
                if line is not None:  # Check if value is not None
                    line_item = QTreeWidgetItem([line])
                    if line in line_machine_map:
                        for machine in line_machine_map[line]:
                            if machine is not None:  # Check if value is not None
                                machine_item = QTreeWidgetItem([machine])
                                if machine in machine_problem_map:
                                    for problem in machine_problem_map[machine]:
                                        if problem is not None:  # Check if value is not None
                                            problem_item = QTreeWidgetItem([problem])
                                            if problem in problem_caction_map:
                                                for corrective_action in problem_caction_map[problem]:
                                                    if corrective_action is not None:  # Check if value is not None
                                                        corrective_action_item = QTreeWidgetItem([corrective_action])
                                                        problem_item.addChild(corrective_action_item)
                                            machine_item.addChild(problem_item)
                                line_item.addChild(machine_item)
                    area_item.addChild(line_item)
            tree_widget.addTopLevelItem(area_item)

    # Restore expanded state after updating
    for item_name, is_expanded in expanded_states.items():
        items = tree_widget.findItems(item_name, QtCore.Qt.MatchExactly)
        if items:
            items[0].setExpanded(is_expanded)

    tree_widget.itemClicked.connect(
        lambda item: update_labels(item, area_value_line_edit_short, area_value_line_edit_full,
                                   line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                                   machine_line_edit, problem_line_edit, corrective_action_line_edit))


def add_data_to_database(table_widget, area_value_line_edit_short, area_value_line_edit_full,
                         line_value_line_edit_short,
                         line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                         corrective_action_line_edit, tree_widget):
    try:
        area_short = area_value_line_edit_short.text().strip()
        area_full = area_value_line_edit_full.text().strip()
        line_short = line_value_line_edit_short.text().strip()
        line_full = line_value_line_edit_full.text().strip()
        time_avail = time_value_line_edit.text().strip()
        machine_name = machine_line_edit.text().strip()
        problem_desc = problem_line_edit.text().strip()
        corrective_action_desc = corrective_action_line_edit.text().strip()
        if (line_full and line_short and time_avail and not machine_name
                and not problem_desc and not corrective_action_desc):
            with connect_to_database() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                area_row = cursor.fetchone()
                ano = area_row[0]
                cursor.execute("SELECT * FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                               (ano, line_short, line_full, time_avail))
                line_row = cursor.fetchone()
                if line_row:
                    QMessageBox.information(None, "Failed", "The Line already exists in the database.")
                    return
                else:
                    cursor.execute("INSERT INTO LINE (ANO, LNAME, LONAME, TAVAIL) VALUES (?, ?, ?, ?)",
                                   (ano, line_short, line_full, time_avail))
                    conn.commit()
                    QMessageBox.information(None, "Success", "The Line is added successfully to the database.")
                    update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                       line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                                       machine_line_edit, problem_line_edit, corrective_action_line_edit)
                    delegate = CompleterDelegate(table_widget)
                    table_widget.setItemDelegate(delegate)
            return
        elif line_full and line_short and time_avail and machine_name and not problem_desc and not corrective_action_desc:
            with connect_to_database() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                area_row = cursor.fetchone()
                ano = area_row[0]
                cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                               (ano, line_short, line_full, time_avail))
                line_row = cursor.fetchone()
                lno = line_row[0]
                cursor.execute("SELECT * FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                               (ano, lno, machine_name))
                machine_row = cursor.fetchone()
                if machine_row:
                    QMessageBox.information(None, "Failed", "The Machine already exists in the database.")
                    return
                else:
                    cursor.execute("INSERT INTO MACHINE (ANO, LNO, MNAME) VALUES (?, ?, ?)", (ano, lno, machine_name))
                    conn.commit()
                    QMessageBox.information(None, "Success", "The Machine added successfully to the database.")
                    update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                       line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                                       machine_line_edit, problem_line_edit, corrective_action_line_edit)
                    delegate = CompleterDelegate(table_widget)
                    table_widget.setItemDelegate(delegate)
            return
        elif line_full and line_short and time_avail and machine_name and problem_desc and not corrective_action_desc:
            with connect_to_database() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                area_row = cursor.fetchone()
                ano = area_row[0]
                cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL= ?",
                               (ano, line_short, line_full, time_avail))
                line_row = cursor.fetchone()
                lno = line_row[0]
                cursor.execute("SELECT MNO FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                               (ano, lno, machine_name))
                machine_row = cursor.fetchone()
                mno = machine_row[0]
                cursor.execute("SELECT * FROM PROBLEM WHERE ANO = ? AND LNO = ? AND MNO = ? AND PDESC = ?",
                               (ano, lno, mno, problem_desc))
                problem_row = cursor.fetchone()
                if problem_row:
                    QMessageBox.information(None, "Failed", "The Problem already exists in the database.")
                    return
                else:
                    cursor.execute("INSERT INTO PROBLEM (ANO, LNO, MNO, PDESC) VALUES (?, ?, ?, ?)",
                                   (ano, lno, mno, problem_desc))
                    conn.commit()
                    QMessageBox.information(None, "Success", "The Problem added successfully to the database.")
                    update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                       line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                                       machine_line_edit, problem_line_edit, corrective_action_line_edit)
                    delegate = CompleterDelegate(table_widget)
                    table_widget.setItemDelegate(delegate)
            return
        elif line_full and line_short and time_avail and machine_name and problem_desc and corrective_action_desc:
            with connect_to_database() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                area_row = cursor.fetchone()
                ano = area_row[0]
                cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                               (ano, line_short, line_full, time_avail))
                line_row = cursor.fetchone()
                lno = line_row[0]
                cursor.execute("SELECT MNO FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                               (ano, lno, machine_name))
                machine_row = cursor.fetchone()
                mno = machine_row[0]
                cursor.execute("SELECT PNO FROM PROBLEM WHERE ANO = ? AND LNO = ? AND MNO = ? AND PDESC = ?",
                               (ano, lno, mno, problem_desc))
                problem_row = cursor.fetchone()
                pno = problem_row[0]
                cursor.execute(
                    "SELECT * FROM CACTION WHERE ANO = ? AND LNO = ? AND MNO = ? AND PNO = ? AND ADESC = ?",
                    (ano, lno, mno, pno, corrective_action_desc))
                caction_row = cursor.fetchone()
                if caction_row:
                    QMessageBox.information(None, "Failed", "The Corrective action already exists in the database.")
                    return
                else:
                    cursor.execute("INSERT INTO CACTION (ANO, LNO, MNO, PNO, ADESC) VALUES (?, ?, ?, ?, ?)",
                                   (ano, lno, mno, pno, corrective_action_desc))
                    conn.commit()
                    QMessageBox.information(None, "Success",
                                            "The Corrective action is added successfully to the database.")
                    update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                       line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                                       machine_line_edit, problem_line_edit, corrective_action_line_edit)
                    delegate = CompleterDelegate(table_widget)
                    table_widget.setItemDelegate(delegate)
            return
    except sqlite3.Error as e:
        error_message = str(e)
        if "UNIQUE constraint failed" in error_message:
            QMessageBox.critical(None, "Error", "The data you're trying to add already exists in the database. "
                                                "Please ensure that all fields are unique.")
        else:
            QMessageBox.critical(None, "Error", f"SQLite Error: {str(e)}")
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            QMessageBox.critical(None, "Failed", "Cannot add data all at once. add data one by one.")
        else:
            QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")


def remove_data_from_database(table_widget, area_value_line_edit_short, area_value_line_edit_full,
                              line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                              machine_line_edit, problem_line_edit, corrective_action_line_edit, tree_widget):
    try:
        confirmation = QMessageBox.question(None, "Confirmation",
                                            "Are you sure you want to delete this data?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            area_short = area_value_line_edit_short.text().strip()
            area_full = area_value_line_edit_full.text().strip()
            line_short = line_value_line_edit_short.text().strip()
            line_full = line_value_line_edit_full.text().strip()
            time_avail = time_value_line_edit.text().strip()
            machine_name = machine_line_edit.text().strip()
            problem_desc = problem_line_edit.text().strip()
            corrective_action_desc = corrective_action_line_edit.text().strip()
            if (line_full and line_short and time_avail and not machine_name
                    and not problem_desc and not corrective_action_desc):
                with connect_to_database() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                    area_row = cursor.fetchone()
                    ano = area_row[0]
                    cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                                   (ano, line_short, line_full, time_avail))
                    line_row = cursor.fetchone()
                    lno = line_row[0]
                    if not line_row:
                        QMessageBox.information(None, "Failed", "The Line does not exist in the database.")
                        return
                    else:
                        cursor.execute("SELECT COUNT(*) as C FROM MACHINE WHERE ANO = ? AND LNO = ?",
                                       (ano, lno))
                        machine_count = cursor.fetchone()[0]
                        if machine_count > 0:
                            QMessageBox.information(None, "Warning",
                                                    "There are machines associated with this line. Please delete the "
                                                    "machines first.")
                            return
                        else:
                            cursor.execute("DELETE FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                                           (ano, line_short, line_full, time_avail))
                            conn.commit()
                            QMessageBox.information(None, "Success",
                                                    "The Line is deleted successfully from the database.")
                            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                               line_value_line_edit_short, line_value_line_edit_full,
                                               time_value_line_edit,
                                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
                            delegate = CompleterDelegate(table_widget)
                            table_widget.setItemDelegate(delegate)
                return
            elif (line_full and line_short and time_avail and machine_name
                  and not problem_desc and not corrective_action_desc):
                with connect_to_database() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                    area_row = cursor.fetchone()
                    ano = area_row[0]
                    cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL = ?",
                                   (ano, line_short, line_full, time_avail))
                    line_row = cursor.fetchone()
                    lno = line_row[0]
                    cursor.execute("SELECT MNO FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                                   (ano, lno, machine_name))
                    machine_row = cursor.fetchone()
                    mno = machine_row[0]
                    if not machine_row:
                        QMessageBox.information(None, "Failed", "The Machine does not exist in the database.")
                        return
                    else:
                        cursor.execute("SELECT COUNT(*) FROM PROBLEM WHERE ANO = ? AND LNO = ? AND MNO = ?",
                                       (ano, lno, mno))
                        problem_count = cursor.fetchone()[0]
                        if problem_count > 0:
                            QMessageBox.information(None, "Warning",
                                                    "There are problems associated with this machine. Please delete the problems first.")
                            return
                        else:
                            cursor.execute("DELETE FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                                           (ano, lno, machine_name))
                            conn.commit()
                            QMessageBox.information(None, "Success",
                                                    "The Machine deleted successfully from the database.")
                            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                               line_value_line_edit_short, line_value_line_edit_full,
                                               time_value_line_edit,
                                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
                            delegate = CompleterDelegate(table_widget)
                            table_widget.setItemDelegate(delegate)
                return
            elif (line_full and line_short and time_avail and machine_name
                  and problem_desc and not corrective_action_desc):
                with connect_to_database() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?", (area_short, area_full))
                    area_row = cursor.fetchone()
                    ano = area_row[0]
                    cursor.execute("SELECT LNO FROM LINE WHERE ANO = ? AND LNAME = ? AND LONAME = ? AND TAVAIL= ?",
                                   (ano, line_short, line_full, time_avail))
                    line_row = cursor.fetchone()
                    lno = line_row[0]
                    cursor.execute("SELECT MNO FROM MACHINE WHERE ANO = ? AND LNO = ? AND MNAME = ?",
                                   (ano, lno, machine_name))
                    machine_row = cursor.fetchone()
                    mno = machine_row[0]
                    cursor.execute("SELECT PNO FROM PROBLEM WHERE ANO = ? AND LNO = ? AND MNO = ? AND PDESC = ?",
                                   (ano, lno, mno, problem_desc))
                    problem_row = cursor.fetchone()
                    pno = machine_row[0]
                    if not problem_row:
                        QMessageBox.information(None, "Failed", "The Problem does not exist in the database.")
                        return
                    else:
                        cursor.execute("SELECT COUNT(*) FROM CACTION WHERE ANO = ? AND LNO = ? AND MNO = ? AND PNO = ?",
                                       (ano, lno, mno, pno))
                        caction_count = cursor.fetchone()[0]
                        if caction_count > 0:
                            QMessageBox.information(None, "Warning",
                                                    "There are corrective actions associated with this problem. Please delete the corrective actions first.")
                            return
                        else:
                            cursor.execute("DELETE FROM PROBLEM WHERE ANO = ? AND LNO = ? AND MNO = ? AND PDESC = ?",
                                           (ano, lno, mno, problem_desc))
                            conn.commit()
                            QMessageBox.information(None, "Success",
                                                    "The Problem deleted successfully from the database.")
                            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                               line_value_line_edit_short, line_value_line_edit_full,
                                               time_value_line_edit,
                                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
                            delegate = CompleterDelegate(table_widget)
                            table_widget.setItemDelegate(delegate)
                return
            elif (line_full and line_short and time_avail and machine_name
                  and problem_desc and corrective_action_desc):
                with connect_to_database() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        '''
                            SELECT ANO, LNO, MNO, PNO
                            FROM CACTION
                            WHERE ANO IN (SELECT ANO FROM AREA WHERE ANAME = ? AND AONAME = ?)
                              AND LNO IN (SELECT LNO FROM LINE WHERE LNAME = ? AND LONAME = ? AND TAVAIL = ?)
                              AND MNO IN (SELECT MNO FROM MACHINE WHERE MNAME = ?)
                              AND PNO IN (SELECT PNO FROM PROBLEM WHERE PDESC = ?)
                        ''',
                        (area_short, area_full, line_short, line_full, time_avail, machine_name, problem_desc))
                    caction_rows = cursor.fetchall()
                    found = False
                    for ano, lno, mno, pno in caction_rows:
                        cursor.execute(
                            "SELECT CNO FROM CACTION WHERE ANO = ? AND LNO = ? AND MNO = ? AND PNO = ? AND ADESC = ?",
                            (ano, lno, mno, pno, corrective_action_desc))
                        existing_action = cursor.fetchone()
                        if existing_action:
                            found = True
                            cursor.execute(
                                "DELETE FROM CACTION WHERE ANO = ? AND LNO = ? AND MNO = ? AND PNO = ? AND ADESC = ?",
                                (ano, lno, mno, pno, corrective_action_desc))
                            conn.commit()
                            QMessageBox.information(None, "Success",
                                                    "The Corrective action is deleted successfully from the database.")
                            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                                               line_value_line_edit_short, line_value_line_edit_full,
                                               time_value_line_edit,
                                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
                            delegate = CompleterDelegate(table_widget)
                            table_widget.setItemDelegate(delegate)
                    if not found:
                        QMessageBox.information(None, "Not Found",
                                                "The specified Corrective action does not exist in the database.")
                    return
        else:
            return
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Error", f"SQLite Error: {str(e)}")
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            QMessageBox.critical(None, "Failed", "Can't delete data all at once. Delete data one by one.")
        else:
            QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")
