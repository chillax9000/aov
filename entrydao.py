import os
import sqlite3
import entry
import datetime as dt

db_path_default = os.path.join(os.path.dirname(__file__), "data", "data.db")


def _get_id(record):
    id, text, datetime_str = record
    return id


def _record_to_entry(record):
    id, text, datetime_str = record
    return entry.Entry(text, dt.datetime.fromisoformat(datetime_str))


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
        c.execute("CREATE TABLE entries (id INTEGER PRIMARY KEY, text TEXT, datetime timestamp)")
        conn.commit()
        conn.close()

    def write(self, entry):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"""
        INSERT INTO entries(text, datetime) VALUES ("{entry.text}", "{entry.datetime.isoformat()}")
        """)
        conn.commit()
        conn.close()

    def get_all(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM entries")
        records = c.fetchall()
        conn.close()
        return [(_get_id(record), _record_to_entry(record)) for record in records]

    def get(self, id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"SELECT * FROM entries WHERE id == {id}")
        record = c.fetchone()
        conn.close()
        return _record_to_entry(record) if record else None

    def update(self, id, entry):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"""UPDATE entries SET TEXT = "{entry.text}" WHERE id = {id}""")
        conn.commit()
        conn.close()

    def delete(self, id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"""DELETE FROM entries WHERE id = {id}""")
        nb_row_deleted = conn.total_changes
        conn.commit()
        conn.close()
        return nb_row_deleted
