import os
import sqlite3


class BaseMigrator:
    def script(self):
        raise NotImplementedError

    def get_version(self):
        raise NotImplementedError

    def set_version(self, n_version):
        raise NotImplementedError

    def _do_apply(self, version_apply):
        print(f"Applying migration {version_apply}")
        try:
            self.script()
        except Exception as e:
            # todo: rollback
            print("Error occured, check db state...")
            print(e)
        else:
            self.set_version(version_apply)
            return True
        return False

    def apply(self, version_apply):
        """:return True iff migration was successfully applied"""
        try:
            version_read = self.get_version()
        except:
            if version_apply == 0:
                return self._do_apply(version_apply)
            else:
                print("Could not get database version, aborting migration")
        else:
            if version_apply == version_read + 1:
                return self._do_apply(version_apply)
            else:
                print(f"Will not apply migration {version_apply} to database {version_read}")
        return False


class SqliteMigrator(BaseMigrator):
    def __init__(self, sqlite_db_path, stamp_path=None):
        def get_sqlite_conn():
            if not os.path.exists(os.path.dirname(sqlite_db_path)):
                os.makedirs(os.path.dirname(sqlite_db_path))
            return sqlite3.connect(sqlite_db_path)

        self.get_sqlite_conn = get_sqlite_conn
        self.stamp_path = stamp_path if stamp_path else os.path.join(os.path.dirname(sqlite_db_path), ".version_stamp")

    def get_version(self):
        with open(self.stamp_path) as f:
            return int(f.read())

    def set_version(self, n_version):
        with open(self.stamp_path, "w") as f:
            f.write(str(n_version))
