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
                 CAST(SUBSTR(l.LNAME, 6) AS INTEGER);
    """)
    single_map = {}
    for area, line, machine, problem, corrective_action in cursor.fetchall():
        single_map.setdefault(area, {}).setdefault(line, {}).setdefault(machine, {}).setdefault(problem, []).append(corrective_action)
    return single_map


def extract_full_mappings(single_map):
    area_line_map = {}
    line_machine_map = {}
    machine_problem_map = {}
    problem_caction_map = {}
    for area, area_data in single_map.items():
        for line, line_data in area_data.items():
            if line_data is not None:
                area_line_map.setdefault(area, []).append(line)
            for machine, machine_data in line_data.items():
                if machine_data is not None:
                    line_machine_map.setdefault(line, []).append(machine)
                for problem, corrective_actions in machine_data.items():
                    machine_problem_map.setdefault(machine, []).append(problem)
                    if corrective_actions is not None:
                        for corrective_action in corrective_actions:
                            problem_caction_map.setdefault(problem, []).append(corrective_action)
                    else:
                        problem_caction_map.setdefault(problem, [])
    return area_line_map, line_machine_map, machine_problem_map, problem_caction_map

if __name__ == '__main__':
    with connect_to_database() as conn:
        m = create_full_map(conn)
        # print(m)
        al, lm, mp, pc = extract_full_mappings(m)
        print(al)
        print(lm)
        print(mp)
        print(pc)

def extract_machines_and_problems_of_area(conn, area):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.MNAME, p.PDESC
        FROM AREA a 
        JOIN LINE l ON a.ANO = l.ANO
        JOIN MACHINE m ON l.LNO = m.LNO
        JOIN PROBLEM p ON m.MNO = p.MNO
        WHERE a.ANAME = ?
    """, (area,))
    machines_and_problems = [(row[0], row[1]) for row in cursor.fetchall()]
    return machines_and_problems
