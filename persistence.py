import sqlite3
import json

conn = sqlite3.connect('abyss_lineage.db')

def init_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS lineage
                 (id INTEGER PRIMARY KEY, seed TEXT, results TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

def add_lineage_entry(seed: str, results: dict):
    c = conn.cursor()
    c.execute("INSERT INTO lineage (seed, results) VALUES (?, ?)", (seed, json.dumps(results)))
    conn.commit()
    return c.lastrowid

def get_lineage_tree() -> list:
    c = conn.cursor()
    c.execute("SELECT * FROM lineage ORDER BY timestamp")
    return [{"id": row[0], "seed": row[1], "results": json.loads(row[2]), "time": row[3]} for row in c.fetchall()]
