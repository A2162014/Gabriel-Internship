tables = []
barcharts = []

column_headers = ["DATE", "TIME", "AM/PM", "CLOSING TIME", "AM/PM", "TOTAL TIME", "AREA",
                  "LINE", "MACHINE", "PROBLEM", "STATUS", "INCHARGE", "CORRECTIVE ACTION"]

area_stats_header = ["Shox DA & FA", "FF FA", "OT Cell", "IT GRD"]

lines1_stats_header = ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9",
                       "DA-10", "DA-11", "Valve Assly", "SA-3", "SA-5", "Welding"]

lines2_stats_header = ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF", "TFF-2"]

lines34_stats_header = ["Cell-1", "Cell-2", "Cell-3", "Cell-4", "Cell-5", "Cell-6",
                        "Cell-7", "Cell-8", "Cell-9", "Cell-10", "Cell-11", "Cell-12", "ITG-1", "ITG-2"]

area_line_map_table = {
    "SHOX": ["DA-1", "DA-2", "DA-3", "DA-4", "DA-5", "DA-7", "DA-9", "DA-10", "DA-11", "VALVE ASSLY",
             "SA-3", "SA-5", "WELDING"],
    "FFFA": ["FA-1", "FA-2", "FA-3", "FA-4", "FA-5", "FA-6", "FA-7", "TFF-1", "TFF-2"],
    "OT CELL": ["CELL-1", "CELL-2", "CELL-3", "CELL-4", "CELL-5", "CELL-6",
                "CELL-7", "CELL-8", "CELL-9", "CELL-10", "CELL-11", "CELL-12"],
    "IT GRD": ["ITG-1", "ITG-2"]
}

time_availability = {
    "SHOX": {"DA-1": 880, "DA-2": 1260, "DA-3": 1260, "DA-4": 1260, "DA-5": 880,
             "DA-7": 1260, "DA-9": 880, "DA-10": 880, "DA-11": 1260,
             "VALVE ASSLY": 880, "SA-3": 1260, "SA-5": 440, "WELDING": 1260},
    "FFFA": {"FA-1": 1260, "FA-2": 1260, "FA-3": 1260, "FA-4": 1260,
             "FA-5": 1260, "FA-6": 880, "FA-7": 440, "TFF-1": 1260, "TFF-2": 880},
    "OT CELL": {"CELL-1": 1260, "CELL-2": 1260, "CELL-3": 1260, "CELL-4": 1260,
                "CELL-5": 1260, "CELL-6": 1260, "CELL-7": 1260, "CELL-8": 1260,
                "CELL-9": 1260, "CELL-10": 1260, "CELL-11": 1260, "CELL-12": 1260},
    "IT GRD": {"ITG-1": 1260, "ITG-2": 880}
}
