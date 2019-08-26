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


def update(id_entry, dao):
    id, old_text = dao.get(id_entry)
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(old_text)

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        entry_ = entry.Entry.from_file(buffer_path)
        dao.update(id_entry, entry_)


if __name__ == "__main__":
    dao = entrydao.EntryDao()
    go_on = True
    while go_on:
        ans = input()
        if ans in ("w", "write", "new"):
            write_new(dao)

        if ans in ("l", "list"):
            for row in dao.get_all():
                print(row)

        if ans in ("u", "update"):
            id_entry = int(input("entry id:"))
            update(id_entry, dao)

        if ans in ("q", "quit"):
            go_on = False

        if ans in ("init"):
            shutil.rmtree(os.path.dirname(entrydao.db_path_default))
            dao.init_table()
