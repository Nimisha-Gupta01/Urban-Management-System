"""
init_db.py — Initialize the SQLite database
Runs schema.sql, triggers.sql, then seed_data.sql in order.
Usage:  python init_db.py
        python init_db.py --reset   (drops existing DB first)
"""

import sqlite3
import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'data', 'traffic.db')
SQL_DIR  = os.path.join(BASE_DIR, 'sql')

SQL_FILES = [
    ('schema.sql',    'DDL: tables, indexes, constraints'),
    ('triggers_ddl.sql', 'Views, triggers (DDL only — no transaction demos)'),
    ('seed_data.sql', 'Sample data (Bengaluru roads/junctions/incidents)'),
]

# triggers.sql contains both DDL (CREATE VIEW / TRIGGER) and DML transaction demos.
# We extract only the DDL portion up to the TRANSACTIONS section for init,
# then apply the transaction demos after seed data is loaded.
TRANSACTION_DEMO_MARKER = '-- TRANSACTIONS — ACID DEMONSTRATION'


def extract_triggers_ddl(src_path, dst_path):
    """Write triggers_ddl.sql containing only DDL (views + triggers), not the demo transactions."""
    with open(src_path, 'r') as f:
        content = f.read()
    # Keep everything before the TRANSACTIONS section
    marker_pos = content.find(TRANSACTION_DEMO_MARKER)
    if marker_pos == -1:
        ddl = content
    else:
        # Back-track past the comment-block separator line
        section_start = content.rfind('-- =====', 0, marker_pos)
        ddl = content[:section_start] if section_start != -1 else content[:marker_pos]
    with open(dst_path, 'w') as f:
        f.write(ddl)


def run_sql_file(conn, filepath, label):
    print(f"  → {label} ... ", end='', flush=True)
    with open(filepath, 'r') as f:
        sql = f.read()
    # Execute statement-by-statement to surface individual errors
    conn.executescript(sql)
    print("OK")


def init(reset=False):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    print(f"Initialising database: {DB_PATH}\n")

    # Pre-process triggers.sql → triggers_ddl.sql (views + triggers only)
    triggers_src = os.path.join(SQL_DIR, 'triggers.sql')
    triggers_ddl = os.path.join(SQL_DIR, 'triggers_ddl.sql')
    extract_triggers_ddl(triggers_src, triggers_ddl)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")

    for filename, label in SQL_FILES:
        path = os.path.join(SQL_DIR, filename)
        if not os.path.exists(path):
            print(f"  ✗  File not found: {path}")
            sys.exit(1)
        try:
            run_sql_file(conn, path, label)
        except sqlite3.Error as e:
            print(f"FAILED\n  Error in {filename}: {e}")
            conn.close()
            sys.exit(1)

    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()

    # Clean up temp file
    if os.path.exists(triggers_ddl):
        os.remove(triggers_ddl)

    print(f"\nDatabase ready at: {DB_PATH}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialise traffic.db')
    parser.add_argument('--reset', action='store_true',
                        help='Delete existing DB and recreate from scratch')
    args = parser.parse_args()
    init(reset=args.reset)
