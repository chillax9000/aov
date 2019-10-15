import os
import sqlite3
import entry
import datetime as dt

db_base_path_default = os.path.join(os.path.dirname(__file__), "data")
db_file_name_default = "data.db"


def _get_id(record):
    id, text, creation_datetime_str, update_datetime_str, topic = record
    return id


def _record_to_entry(record):
    id, text, creation_datetime_str, update_datetime_str, topic = record
    return entry.Entry(
            text,
            dt.datetime.fromisoformat(creation_datetime_str),
            dt.datetime.fromisoformat(update_datetime_str),
            topic
            )


class EntryDao:
    def __init__(self, db_name=None, db_base_path=db_base_path_default):
        self.db_name = db_name if db_name else "default"
        self.db_path = os.path.join(db_base_path, self.db_name, db_file_name_default)

    def get_conn(self):
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
        return sqlite3.connect(self.db_path)

    def write(self, entry):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"""
        INSERT INTO entries(text, creation_datetime, update_datetime, topic) 
        VALUES ("{entry.text}", "{entry.creation_datetime.isoformat()}", "{entry.update_datetime.isoformat()}", "{entry.topic}")
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
        c.execute(f"""
        UPDATE entries SET (text, update_datetime, topic) 
        = ("{entry.text}", "{entry.update_datetime.isoformat()}", "{entry.topic}") 
        WHERE id = {id}
        """)
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

    def get_containing(self, s):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"SELECT * FROM entries WHERE instr(TEXT, '{s}')")
        records = c.fetchall()
        conn.close()
        return [(_get_id(record), _record_to_entry(record)) for record in records]

    def get_topics(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute(f"SELECT topic FROM entries")
        records = c.fetchall()
        conn.close()
        return set(record[0] for record in records)
