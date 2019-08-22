import os
import shutil
import subprocess
import entry
import entrydao
import tempfile


def write_new(dao):
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        entry_ = entry.Entry.from_file(buffer_path)
        dao.write(entry_)


if __name__ == "__main__":
    dao = entrydao.EntryDao()
    go_on = True
    while go_on:
        ans = input()
        if ans in ("w", "write"):
            write_new(dao)
        if ans in ("l", "list"):
            for row in dao.get_all():
                print(row)
        if ans in ("q", "quit"):
            go_on = False

        if ans in ("init"):
            shutil.rmtree(os.path.dirname(entrydao.db_path_default))
            dao.init_table()
