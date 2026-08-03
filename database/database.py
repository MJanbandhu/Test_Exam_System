import sqlite3
import os
from config import Config

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    db_dir = os.path.dirname(Config.DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
