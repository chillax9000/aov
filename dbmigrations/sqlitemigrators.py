from dbmigrations.migrator import SqliteMigrator


class InitMigrator(SqliteMigrator):
    def script(self):
        conn = self.get_sqlite_conn()
        c = conn.cursor()
        c.execute("""
                  CREATE TABLE entries (
                  id INTEGER PRIMARY KEY, 
                  text TEXT, 
                  creation_datetime timestamp, 
                  update_datetime timestamp);
                  """)
        conn.commit()
        conn.close()


class AddTopicMigrator(SqliteMigrator):
    def script(self):
        conn = self.get_sqlite_conn()
        c = conn.cursor()
        c.execute("""
                  ALTER TABLE entries
                  ADD COLUMN topic TEXT;
                  """)
        conn.commit()
        conn.close()
