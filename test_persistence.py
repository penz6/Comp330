import sqlite3
import os
from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
from zscore_calculator import (
    calculate_section_stats,
    calculate_group_stats,
    compute_z_score,
    compute_p_value,
    is_significant
)

def main():
    DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(""" 
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            lname TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            mean_gpa REAL NOT NULL,
            count INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            mean_gpa REAL NOT NULL,
            stddev REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            grade TEXT NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY(section_id) REFERENCES Sections(id),
            FOREIGN KEY(student_id) REFERENCES Students(id)
        );
        CREATE TABLE IF NOT EXISTS ZScores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            z_score REAL,
            p_value REAL,
            significant INTEGER,
            threshold REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(section_id) REFERENCES Sections(id)
        );
    """)

    # 1. Load run → groups → sections
    run_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     "..", "COMSC330_POC_Data", "Runs", "SPRING25.RUN")
    )
    grp_files = runReader(run_file)
    sec_files = grpReader(run_file, grp_files)
    dfs = fileReader.bulkReadSEC(run_file, sec_files)

    # 2. Compute & persist group stats
    group_mean, group_std = calculate_group_stats(dfs)
    c.execute(
        "INSERT OR IGNORE INTO Groups (name, mean_gpa, stddev) VALUES (?, ?, ?)",
        ("SPRING25", group_mean, group_std)
    )

    # 3. Per‐section: compute stats, persist section, students, performances, z‐score
    for sec_file, df in zip(sec_files, dfs):
        sec_name = os.path.splitext(sec_file)[0]
        sec_mean, sec_count = calculate_section_stats(df)
        c.execute(
            "INSERT OR IGNORE INTO Sections (name, mean_gpa, count) VALUES (?, ?, ?)",
            (sec_name, sec_mean, sec_count)
        )
        sec_id = c.execute(
            "SELECT id FROM Sections WHERE name=?", (sec_name,)
        ).fetchone()[0]

        # students & performances
        for _, row in df.iterrows():
            c.execute(
                "INSERT OR IGNORE INTO Students (fname, lname, student_id) VALUES (?, ?, ?)",
                (row["FName"], row["LName"], row["ID"])
            )
            stu_id = c.execute(
                "SELECT id FROM Students WHERE student_id=?", (row["ID"],)
            ).fetchone()[0]
            cat = ("good" if row["Grade"] in ("A", "A-")
                   else "bad" if row["Grade"] in ("F", "D-")
                   else None)
            c.execute(
                "INSERT INTO Performances (section_id, student_id, grade, category) VALUES (?, ?, ?, ?)",
                (sec_id, stu_id, row["Grade"], cat)
            )

        # z‐score
        try:
            z = compute_z_score(sec_mean, group_mean, group_std)
            p = compute_p_value(z)
            sig = is_significant(z)
        except ValueError:
            z = p = None
            sig = False
        c.execute(
            "INSERT INTO ZScores (section_id, z_score, p_value, significant, threshold) VALUES (?, ?, ?, ?, ?)",
            (sec_id, z, p, int(sig), 2.0)
        )

    conn.commit()

    # retrieval tests
    for tbl in ("Students", "Sections", "Groups", "Performances", "ZScores"):
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"{tbl}:", c.fetchone()[0])

    conn.close()
    print(f"Test DB created at {DB_PATH}")

if __name__ == "__main__":
    main()
