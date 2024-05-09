import os
import sqlite3

tables = []
barcharts = []

column_headers = [
    "MONTH", "DATE", "TIME", "AM/PM", "CLOSING TIME", "AM/PM", "TOTAL TIME", "AREA",
    "LINE", "MACHINE", "PROBLEM", "STATUS", "INCHARGE", "CORRECTIVE ACTION"
]


def connect_to_database():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(current_dir, 'database.db')
    return sqlite3.connect(db_file)


def fetch_values(conn, query, params=None):
    cursor = conn.cursor()
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)
    return [row[0].strip() for row in cursor.fetchall()]


def fetch_lonames_for_ano(conn, ano):
    return fetch_values(conn, "SELECT LONAME FROM LINE WHERE ANO = ?", (ano,))


def fetch_area_line_data(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.ANAME, l.LNAME 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
    """)
    return [(area.strip(), line.strip()) for area, line in cursor.fetchall()]


def fetch_area_line_data_tab2(conn, parent_text, item_text):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.AONAME, l.LONAME, l.TAVAIL 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
        WHERE a.ANAME = ? AND l.LNAME = ?
    """, (parent_text, item_text))
    return cursor.fetchone()


def fetch_line_machine_data(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.LNAME, m.MNAME
        FROM LINE l
        JOIN MACHINE m ON l.LNO = m.LNO
    """)
    return [(line.strip(), machine.strip()) for line, machine in cursor.fetchall()]


def fetch_machine_problem_data(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.MNAME, p.PDESC
        FROM MACHINE m
        JOIN PROBLEM p ON m.MNO = p.MNO
    """)
    return [(machine.strip(), problem.strip()) for machine, problem in cursor.fetchall()]


def fetch_problem_caction_data(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.PDESC, c.ADESC
        FROM PROBLEM p
        JOIN CACTION c ON p.PNO = c.PNO
    """)
    return [(problem.strip(), corrective_action.strip()) for problem, corrective_action in cursor.fetchall()]


def create_area_line_map(area_line_data):
    area_line_map = {}
    for area, line in area_line_data:
        area_line_map.setdefault(area, []).append(line)
    return area_line_map


def create_line_machine_map(line_machine_data):
    line_machine_map = {}
    for line, machine in line_machine_data:
        line_machine_map.setdefault(line, []).append(machine)
    return line_machine_map


def create_machine_problem_map(machine_problem_data):
    machine_problem_map = {}
    for machine, problem in machine_problem_data:
        machine_problem_map.setdefault(machine, []).append(problem)
    return machine_problem_map


def create_problem_caction_map(problem_caction_data):
    problem_caction_map = {}
    for problem, corrective_action in problem_caction_data:
        problem_caction_map.setdefault(problem, []).append(corrective_action)
    return problem_caction_map


def create_time_availability(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.ANAME, l.LNAME, l.TAVAIL 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
    """)
    time_availability = {}
    for area, line, tavail in cursor.fetchall():
        time_availability.setdefault(area, {})[line] = tavail
    return time_availability