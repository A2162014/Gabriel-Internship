import sqlite3

from maps import connect_to_database, fetch_area_line_data, create_area_line_map, fetch_line_machine_data, \
    create_line_machine_map, fetch_machine_problem_data, create_machine_problem_map, fetch_problem_caction_data, \
    create_problem_caction_map, fetch_area_line_data_tab2

from styles import treeStyle
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

    print(parent_items)

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


def update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                       line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                       corrective_action_line_edit):
    with connect_to_database() as conn:
        tree_widget.clear()
        area_line_data = fetch_area_line_data(conn)
        area_line_map = create_area_line_map(area_line_data)
        line_machine_data = fetch_line_machine_data(conn)
        line_machine_map = create_line_machine_map(line_machine_data)
        machine_problem_data = fetch_machine_problem_data(conn)
        machine_problem_map = create_machine_problem_map(machine_problem_data)
        problem_caction_data = fetch_problem_caction_data(conn)
        problem_caction_map = create_problem_caction_map(problem_caction_data)
        tree_widget.setStyleSheet(treeStyle)
        tree_widget.setHeaderHidden(True)
        overall_plant_item = QTreeWidgetItem(["Overall Plant"])
        for area, lines in area_line_map.items():
            area_item = QTreeWidgetItem([area])
            for line in lines:
                line_item = QTreeWidgetItem([line])
                if line in line_machine_map:
                    for machine in line_machine_map[line]:
                        machine_item = QTreeWidgetItem([machine])
                        if machine in machine_problem_map:
                            for problem in machine_problem_map[machine]:
                                problem_item = QTreeWidgetItem([problem])
                                if problem in problem_caction_map:
                                    for corrective_action in problem_caction_map[problem]:
                                        corrective_action_item = QTreeWidgetItem([corrective_action])
                                        problem_item.addChild(corrective_action_item)
                                machine_item.addChild(problem_item)
                        line_item.addChild(machine_item)
                area_item.addChild(line_item)
            overall_plant_item.addChild(area_item)
        tree_widget.addTopLevelItem(overall_plant_item)
        tree_widget.itemClicked.connect(
            lambda item: update_labels(item, area_value_line_edit_short, area_value_line_edit_full,
                                       line_value_line_edit_short,
                                       line_value_line_edit_full, time_value_line_edit, machine_line_edit,
                                       problem_line_edit, corrective_action_line_edit))


def add_data_to_database(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                         line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                         corrective_action_line_edit, tree_widget):
    try:
        line_short = line_value_line_edit_short.text().strip()
        line_full = line_value_line_edit_full.text().strip()
        time_avail = time_value_line_edit.text().strip()
        machine_name = machine_line_edit.text().strip()
        problem_desc = problem_line_edit.text().strip()
        corrective_action_desc = corrective_action_line_edit.text().strip()

        if not line_short or not line_full or not time_avail:
            QMessageBox.warning(None, "Error", "Please provide Line Name and Time Availability.")
            return
        elif not machine_name and problem_desc:
            QMessageBox.warning(None, "Error", "Please provide Machine Name.")
            return
        elif not problem_desc and corrective_action_desc:
            QMessageBox.warning(None, "Error", "Please provide Problem Description.")
            return

        with connect_to_database() as conn:
            cursor = conn.cursor()

            # Check if line exists or insert
            cursor.execute("SELECT LNO FROM LINE WHERE LNAME = ? AND LONAME = ?", (line_short, line_full))
            line_row = cursor.fetchone()
            if not line_row:
                cursor.execute("INSERT INTO LINE (LNAME, LONAME, TAVAIL) VALUES (?, ?, ?)",
                               (line_short, line_full, time_avail))
                lno = cursor.lastrowid
            else:
                lno = line_row[0]

            # Check if machine exists or insert
            cursor.execute("SELECT MNO FROM MACHINE WHERE MNAME = ?", (machine_name,))
            machine_row = cursor.fetchone()
            if not machine_row:
                cursor.execute("INSERT INTO MACHINE (LNO, MNAME) VALUES (?, ?)", (lno, machine_name))
                mno = cursor.lastrowid
            else:
                mno = machine_row[0]

            # Check if problem exists or insert
            cursor.execute("SELECT PNO FROM PROBLEM WHERE PDESC = ?", (problem_desc,))
            problem_row = cursor.fetchone()
            if not problem_row:
                cursor.execute("INSERT INTO PROBLEM (MNO, PDESC) VALUES (?, ?)", (mno, problem_desc))
                pno = cursor.lastrowid
            else:
                pno = problem_row[0]

            # Check if corrective action exists or insert
            cursor.execute("SELECT CNO FROM CACTION WHERE ADESC = ?", (corrective_action_desc,))
            caction_row = cursor.fetchone()
            if not caction_row:
                cursor.execute("INSERT INTO CACTION (PNO, ADESC) VALUES (?, ?)", (pno, corrective_action_desc))

            # Commit the transaction
            conn.commit()

            # Inform the user and update tree widget
            QMessageBox.information(None, "Success", "Data added successfully to the database.")
            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                               line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                               machine_line_edit, problem_line_edit, corrective_action_line_edit)

    except sqlite3.Error as e:
        # Handle SQLite errors
        QMessageBox.critical(None, "Error", f"SQLite Error: {str(e)}")
    except Exception as e:
        # Handle other exceptions
        QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")


def update_data_in_database(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                            line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                            corrective_action_line_edit, tree_widget):
    try:
        line_short = line_value_line_edit_short.text().strip()
        line_full = line_value_line_edit_full.text().strip()
        time_avail = time_value_line_edit.text().strip()
        machine_name = machine_line_edit.text().strip()
        problem_desc = problem_line_edit.text().strip()
        corrective_action_desc = corrective_action_line_edit.text().strip()

        with connect_to_database() as conn:
            cursor = conn.cursor()

            if not line_short or not line_full or not time_avail:
                QMessageBox.warning(None, "Error", "Please provide Line Name and Time Availability.")
                return

            if not machine_name and problem_desc:
                QMessageBox.warning(None, "Error", "Please provide Machine Name.")
                return

            if not problem_desc and corrective_action_desc:
                QMessageBox.warning(None, "Error", "Please provide Problem Description.")
                return

            # Check and update line information
            if line_short:
                cursor.execute("SELECT LNAME FROM LINE WHERE LNAME = ?", (line_short,))
                line_row = cursor.fetchone()
                if not line_row:
                    QMessageBox.warning(None, "Error", "Line does not exist. Please add it using the 'Add' function.")
                    return
                else:
                    cursor.execute("UPDATE LINE SET LONAME = ?, TAVAIL = ? WHERE LNAME = ?",
                                   (line_full, time_avail, line_short))

            # Check and update machine information
            if machine_name:
                cursor.execute("SELECT MNAME FROM MACHINE WHERE MNAME = ?", (machine_name,))
                machine_row = cursor.fetchone()
                if not machine_row:
                    QMessageBox.warning(None, "Error", "Machine does not exist. Please add it using the 'Add' function.")
                    return
                else:
                    cursor.execute("UPDATE MACHINE SET LNO = (SELECT LNO FROM LINE WHERE LNAME = ?) WHERE MNAME = ?",
                                   (line_short, machine_name))

            # Check and update problem information
            if problem_desc:
                cursor.execute("SELECT PDESC FROM PROBLEM WHERE PDESC = ?", (problem_desc,))
                problem_row = cursor.fetchone()
                if not problem_row:
                    QMessageBox.warning(None, "Error", "Problem does not exist. Please add it using the 'Add' function.")
                    return
                else:
                    cursor.execute("UPDATE PROBLEM SET MNO = (SELECT MNO FROM MACHINE WHERE MNAME = ?) WHERE PDESC = ?",
                                   (machine_name, problem_desc))

            # Check and update corrective action information
            if corrective_action_desc:
                cursor.execute("SELECT ADESC FROM CACTION WHERE ADESC = ?", (corrective_action_desc,))
                caction_row = cursor.fetchone()
                if not caction_row:
                    QMessageBox.warning(None, "Error", "Corrective action does not exist. Please add it using the 'Add' function.")
                    return
                else:
                    cursor.execute("UPDATE CACTION SET PNO = (SELECT PNO FROM PROBLEM WHERE PDESC = ?) WHERE ADESC = ?",
                                   (problem_desc, corrective_action_desc))

            conn.commit()
            QMessageBox.information(None, "Success", "Data updated successfully in the database.")
            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                               line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Error", f"SQLite Error: {str(e)}")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")


def remove_data_from_database(area_value_line_edit_short, area_value_line_edit_full, line_value_line_edit_short,
                              line_value_line_edit_full, time_value_line_edit, machine_line_edit, problem_line_edit,
                              corrective_action_line_edit, tree_widget):
    try:
        line_short = line_value_line_edit_short.text().strip()
        line_full = line_value_line_edit_full.text().strip()
        machine_name = machine_line_edit.text().strip()
        problem_desc = problem_line_edit.text().strip()
        corrective_action_desc = corrective_action_line_edit.text().strip()

        with connect_to_database() as conn:
            cursor = conn.cursor()

            if machine_name:
                cursor.execute("SELECT MNO FROM MACHINE WHERE MNAME = ?", (machine_name,))
                machine_row = cursor.fetchone()
                if not machine_row:
                    QMessageBox.warning(None, "Error", f"Machine '{machine_name}' does not exist in the database.")
                    return

            if problem_desc:
                cursor.execute("SELECT PNO FROM PROBLEM WHERE PDESC = ?", (problem_desc,))
                problem_row = cursor.fetchone()
                if not problem_row:
                    QMessageBox.warning(None, "Error", f"Problem '{problem_desc}' does not exist in the database.")
                    return

            if corrective_action_desc:
                cursor.execute("SELECT CNO FROM CACTION WHERE ADESC = ?", (corrective_action_desc,))
                caction_row = cursor.fetchone()
                if not caction_row:
                    QMessageBox.warning(None, "Error",
                                        f"Corrective action '{corrective_action_desc}' does not exist in the database.")
                    return

            if not line_short and not line_full:
                QMessageBox.warning(None, "Error", "Please provide Line Name.")
                return

            cursor.execute("DELETE FROM CACTION WHERE PNO IN "
                           "(SELECT PNO FROM PROBLEM WHERE PDESC = ?) "
                           "AND ADESC = ?",
                           (problem_desc, corrective_action_desc))

            cursor.execute("DELETE FROM PROBLEM WHERE PDESC = ?", (problem_desc,))

            if machine_name:
                cursor.execute("DELETE FROM MACHINE WHERE MNAME = ?", (machine_name,))

            if not line_short and not line_full:
                cursor.execute("DELETE FROM LINE WHERE LNAME = ? AND LONAME = ?", (line_short, line_full))

            conn.commit()
            QMessageBox.information(None, "Success", "Data removed successfully from the database.")
            update_tree_widget(tree_widget, area_value_line_edit_short, area_value_line_edit_full,
                               line_value_line_edit_short, line_value_line_edit_full, time_value_line_edit,
                               machine_line_edit, problem_line_edit, corrective_action_line_edit)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")
