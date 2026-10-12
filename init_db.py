"""
init_db.py — Initialize the PostgreSQL database
Runs schema.sql, triggers.sql (DDL only), then seed_data.sql in order.
Usage:  python init_db.py
        python init_db.py --reset   (drops and recreates all tables)
"""

import psycopg2
import os
import sys
import argparse
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR  = os.path.join(BASE_DIR, 'sql')

DB_CONFIG = {
    "host":     os.getenv("PGHOST",     "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
    "dbname":   os.getenv("PGDATABASE", "traffic_db"),
    "user":     os.getenv("PGUSER",     "traffic_user"),
    "password": os.getenv("PGPASSWORD", "traffic_pass"),
}

TRANSACTION_DEMO_MARKER = '-- TRANSACTIONS — ACID DEMONSTRATION'


def wait_for_postgres(retries=15, delay=3):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            print(f"  Waiting for PostgreSQL... ({attempt}/{retries})")
            time.sleep(delay)
    print("Could not connect to PostgreSQL. Exiting.")
    sys.exit(1)


def extract_triggers_ddl(src_path):
    """Return only the DDL portion of triggers.sql (views + triggers, no transaction demos)."""
    with open(src_path, 'r') as f:
        content = f.read()
    marker_pos = content.find(TRANSACTION_DEMO_MARKER)
    if marker_pos == -1:
        return content
    section_start = content.rfind('-- =====', 0, marker_pos)
    return content[:section_start] if section_start != -1 else content[:marker_pos]


def run_sql(conn, sql, label):
    print(f"  → {label} ... ", end='', flush=True)
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("OK")


def drop_all_tables(conn):
    drop_sql = """
    DO $$ DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
        END LOOP;
        FOR r IN (SELECT viewname FROM pg_views WHERE schemaname = 'public') LOOP
            EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.viewname) || ' CASCADE';
        END LOOP;
    END $$;
    """
    with conn.cursor() as cur:
        cur.execute(drop_sql)
    conn.commit()
    print("Dropped all existing tables and views.")


def init(reset=False):
    wait_for_postgres()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False

    try:
        if reset:
            drop_all_tables(conn)

        print(f"\nInitialising database: {DB_CONFIG['dbname']}\n")

        # 1. Schema (tables, indexes, constraints, roles)
        schema_path = os.path.join(SQL_DIR, 'schema.sql')
        with open(schema_path) as f:
            run_sql(conn, f.read(), "DDL: tables, indexes, constraints, roles")

        # 2. Triggers and views (DDL only — strip transaction demo blocks)
        triggers_path = os.path.join(SQL_DIR, 'triggers.sql')
        triggers_ddl = extract_triggers_ddl(triggers_path)
        run_sql(conn, triggers_ddl, "Views, trigger functions, triggers")

        # 3. Seed data — only if Zone table is empty (idempotent restarts)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Zone")
            zone_count = cur.fetchone()[0]

        if zone_count == 0:
            seed_path = os.path.join(SQL_DIR, 'seed_data.sql')
            with open(seed_path) as f:
                run_sql(conn, f.read(), "Sample data (Bengaluru roads/junctions/incidents)")
        else:
            print("  → Sample data already present, skipping seed ... OK")

        # 4. Populate PostGIS geometry from lat/lon
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Junction
                SET geom = ST_MakePoint(longitude, latitude)::GEOGRAPHY
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND geom IS NULL
            """)
        conn.commit()
        print("  → PostGIS geometry populated for Junction ... OK")

        print(f"\nDatabase ready: {DB_CONFIG['dbname']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"\nFAILED: {e}")
        conn.close()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialise PostgreSQL traffic_db')
    parser.add_argument('--reset', action='store_true',
                        help='Drop all tables and recreate from scratch')
    args = parser.parse_args()
    init(reset=args.reset)
