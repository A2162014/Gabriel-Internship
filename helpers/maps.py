import os
import sqlite3

tables = []
barcharts = []

column_headers = [
    "MONTH", "DATE", "TIME", "AM/PM", "CLOSING TIME", "AM/PM", "TOTAL TIME", "AREA",
    "LINE", "MACHINE", "PROBLEM", "STATUS", "INCHARGE", "CORRECTIVE ACTION"
]

stat_headers = ['% of B/D – Locations', 'No of Occurrence – Locations', 'No of Occurrence – Problems in SHOX',
                'No of Occurrence – Problems in FFFA', 'No of Occurrence – Problems in OT CELL',
                'No of Occurrence – Problems in IT GRD', 'MTBF of Locations', 'MTTR of Locations',
                '% OF B/D - Lines in SX Damper & FA', '% OF B/D – Lines in Front Fork Final Assembly',
                '% OF B/D - Lines in OT Cell & IT Grinding', '% OF B/D - Machines in SX Damper & FA',
                '% OF B/D – Machines in Front Fork Final Assembly', '% OF B/D - Machines in OT Cell & IT Grinding']

month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8,
             'September': 9, 'October': 10, 'November': 11, 'December': 12}

current_dir = os.path.dirname(os.path.abspath(__file__))


def connect_to_database():
    global current_dir
    db_file = os.path.join(os.path.dirname(current_dir), 'database.db')
    return sqlite3.connect(db_file)


def fetch_values(conn, query, params=None):
    cursor = conn.cursor()
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)
    return [row[0].strip() for row in cursor.fetchall()]


def fetch_lonames_for_ano(conn, ano):
    return fetch_values(conn, '''
        SELECT LONAME
        FROM LINE
        WHERE ANO = ?
        ORDER BY CASE ANO
                     WHEN 1 THEN SUBSTR(LONAME, 1, 3)
                     WHEN 2 THEN SUBSTR(LONAME, 1, 5)
                     END,
                 CAST(SUBSTR(LONAME, INSTR(LONAME, '-') + 1) AS INTEGER);
    ''', (ano,))


def fetch_area_line_data_tab2(conn, parent_text, item_text):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.AONAME, l.LONAME, l.TAVAIL 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
        WHERE a.ANAME = ? AND l.LNAME = ?
    ''', (parent_text, item_text))
    return cursor.fetchone()


def create_time_availability_lines(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.ANAME, l.LNAME, l.TAVAIL 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
    ''')
    time_availability = {}
    for area, line, tavail in cursor.fetchall():
        time_availability.setdefault(area, {})[line] = tavail
    return time_availability


def create_time_availability_machines(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.ANAME, m.MNAME, l.TAVAIL 
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
        JOIN MACHINE m ON l.LNO = m.LNO
    ''')
    time_availability_machines = {}
    for area, machine, tavail in cursor.fetchall():
        time_availability_machines.setdefault(area, {})[machine] = tavail
    return time_availability_machines


def create_full_map(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.ANAME, l.LNAME, m.MNAME, p.PDESC, c.ADESC
        FROM AREA a
                 LEFT JOIN LINE l ON a.ANO = l.ANO
                 LEFT JOIN MACHINE m ON l.LNO = m.LNO
                 LEFT JOIN PROBLEM p ON m.MNO = p.MNO
                 LEFT JOIN CACTION c ON p.PNO = c.PNO
        ORDER BY a.ANAME,
                 CASE a.ANO
                     WHEN 1 THEN SUBSTR(LONAME, 1, 3)
                     WHEN 2 THEN SUBSTR(LONAME, 1, 5)
                     END,
                 CAST(SUBSTR(l.LNAME, 6) AS INTEGER)
    """)
    area_to_lines = {}
    line_to_machines = {}
    machine_to_problems = {}
    problem_to_actions = {}
    for row in cursor.fetchall():
        area_name, line_name, machine_name, problem_desc, action_desc = row
        if area_name not in area_to_lines:
            area_to_lines[area_name] = {}
        if line_name not in area_to_lines[area_name]:
            area_to_lines[area_name][line_name] = []
        if line_name not in line_to_machines:
            line_to_machines[line_name] = {}
        if machine_name not in line_to_machines[line_name]:
            line_to_machines[line_name][machine_name] = []
        if machine_name not in machine_to_problems:
            machine_to_problems[machine_name] = {}
        if problem_desc not in machine_to_problems[machine_name]:
            machine_to_problems[machine_name][problem_desc] = []
        if problem_desc not in problem_to_actions:
            problem_to_actions[problem_desc] = []
        if action_desc not in problem_to_actions[problem_desc]:
            problem_to_actions[problem_desc].append(action_desc)
    return area_to_lines, line_to_machines, machine_to_problems, problem_to_actions


def extract_lines_machines_problems_of_area(conn, area):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.LNAME, m.MNAME, p.PDESC
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
        JOIN MACHINE m ON l.LNO = m.LNO
        JOIN PROBLEM p ON m.MNO = p.MNO
        WHERE a.ANAME = ?
    """, (area,))
    lines_machines_problems = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    return lines_machines_problems
