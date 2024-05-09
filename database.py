import sqlite3

conn = sqlite3.connect('database.db')

c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for table in tables:
    table_name = table[0]
    c.execute(f"DROP TABLE IF EXISTS {table_name};")

c.executescript('''
    CREATE TABLE AREA (
        ANO INTEGER PRIMARY KEY,
        ANAME TEXT NOT NULL UNIQUE,
        AONAME TEXT NOT NULL UNIQUE
    );
    INSERT INTO AREA (ANAME, AONAME) VALUES ('SHOX', 'Shox DA & FA');
    INSERT INTO AREA (ANAME, AONAME) VALUES ('FFFA', 'FF FA');
    INSERT INTO AREA (ANAME, AONAME) VALUES ('OT CELL', 'OT Cell');
    INSERT INTO AREA (ANAME, AONAME) VALUES ('IT GRD', 'IT GRD');
''')

c.executescript('''
    CREATE TABLE LINE (
        LNO INTEGER PRIMARY KEY,
        ANO INTEGER NOT NULL,
        LNAME TEXT NOT NULL UNIQUE,
        LONAME TEXT NOT NULL UNIQUE,
        TAVAIL INTEGER NOT NULL,
        FOREIGN KEY (ANO) REFERENCES AREA(ANO)
    );
    INSERT INTO LINE (ANO, LNAME, LONAME, TAVAIL) VALUES
    (1, 'DA-1', 'DA-1', '880'),
    (1, 'DA-2','DA-2', '1260'),
    (1, 'DA-3', 'DA-3', '1260'),
    (1, 'DA-4', 'DA-4', '1260'),
    (1, 'DA-5', 'DA-5', '880'),
    (1, 'DA-7', 'DA-7', '1260'),
    (1, 'DA-9', 'DA-9', '880'),
    (1, 'DA-10', 'DA-10', '880'),
    (1, 'DA-11', 'DA-11', '1260'),
    (1, 'VALVE ASSLY', 'Valve Assly', '880'),
    (1, 'SA-3', 'SA-3', '1260'),
    (1, 'SA-5', 'SA-5', '440'),
    (1, 'WELDING', 'Welding', '1260'),
    (2, 'FA-1', 'FA-1', '1260'),
    (2, 'FA-2', 'FA-2', '1260'),
    (2, 'FA-3', 'FA-3', '1260'),
    (2, 'FA-4', 'FA-4', '1260'),
    (2, 'FA-5', 'FA-5', '1260'),
    (2, 'FA-6', 'FA-6', '880'),
    (2, 'FA-7', 'FA-7', '440'),
    (2, 'TFF-1', 'TFF-1', '1260'),
    (2, 'TFF-2', 'TFF-2', '880'),
    (3, 'CELL-1', 'Cell-1', '1260'),
    (3, 'CELL-2', 'Cell-2', '1260'),
    (3, 'CELL-3', 'Cell-3', '1260'),
    (3, 'CELL-4', 'Cell-4', '1260'),
    (3, 'CELL-5', 'Cell-5', '1260'),
    (3, 'CELL-6', 'Cell-6', '1260'),
    (3, 'CELL-7', 'Cell-7', '1260'),
    (3, 'CELL-8', 'Cell-8', '1260'),
    (3, 'CELL-9', 'Cell-9', '1260'),
    (3, 'CELL-10', 'Cell-10', '1260'),
    (3, 'CELL-11', 'Cell-11', '1260'),
    (3, 'CELL-12', 'Cell-12', '1260'),
    (4, 'ITG-1', 'ITG-1', '1260'),
    (4, 'ITG-2', 'ITG-2', '880');
''')

c.executescript('''
    CREATE TABLE MACHINE (
        MNO INTEGER PRIMARY KEY,
        ANO INTEGER NOT NULL,
        LNO INTEGER NOT NULL,
        MNAME TEXT NOT NULL,
        FOREIGN KEY (ANO) REFERENCES AREA(ANO),
        FOREIGN KEY (LNO) REFERENCES LINE(LNO)
    );
    CREATE TABLE PROBLEM (
        PNO INTEGER PRIMARY KEY,
        ANO INTEGER NOT NULL,
        LNO INTEGER NOT NULL,
        MNO INTEGER NOT NULL,
        PDESC TEXT NOT NULL,
        FOREIGN KEY (ANO) REFERENCES AREA(ANO),
        FOREIGN KEY (LNO) REFERENCES LINE(LNO),
        FOREIGN KEY (MNO) REFERENCES MACHINE(MNO)
    );
    CREATE TABLE CACTION (
        CNO INTEGER PRIMARY KEY,
        ANO INTEGER NOT NULL,
        LNO INTEGER NOT NULL,
        MNO INTEGER NOT NULL,
        PNO INTEGER NOT NULL,
        ADESC TEXT NOT NULL,
        FOREIGN KEY (ANO) REFERENCES AREA(ANO),
        FOREIGN KEY (LNO) REFERENCES LINE(LNO),
        FOREIGN KEY (MNO) REFERENCES MACHINE(MNO),
        FOREIGN KEY (PNO) REFERENCES PROBLEM(PNO)
    );
''')

conn.commit()
conn.close()
