import os
import sqlite3

db_path_default = os.path.join(os.path.dirname(__file__), "data", "data.db")


class EntryDao:
    def __init__(self, db_path=db_path_default):
        self.db_path = db_path

    def get_conn(self):
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
        return sqlite3.connect(self.db_path)

    def init_table(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("CREATE TABLE entries (id INTEGER PRIMARY KEY, text TEXT)")
        conn.commit()
        conn.close()

    def write(self, entry):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"""
        INSERT INTO entries(text) VALUES ("{entry.text}")
        """)
        conn.commit()
        conn.close()

    def get_all(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM entries")
        records = c.fetchall()
        conn.close()
        return records

    def get(self, id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"SELECT * FROM entries WHERE id == {id}")
        record = c.fetchone()
        conn.close()
        return record
