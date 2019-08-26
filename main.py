import os
import shutil
import subprocess
from entry import Entry
import entrydao
import tempfile


def write_new(dao):
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        entry_ = Entry.from_file(buffer_path)
        dao.write(entry_)


def update(id_entry, dao):
    entry_old = dao.get(id_entry)
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(entry_old.text)

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        entry_new = Entry.from_file(buffer_path)
        dao.update(id_entry, entry_new)


if __name__ == "__main__":
    dao = entrydao.EntryDao()
    go_on = True
    while go_on:
        ans = input()
        ans_splitted = ans.split()
        ans_head = ans_splitted[0] if len(ans_splitted) > 0 else None
        ans_tail = ans_splitted[1:]
        if ans in ("n", "new", "w", "write"):
            write_new(dao)

        if ans in ("l", "list"):
            for id, entry in dao.get_all():
                print(f"{id}.", entry.text.strip())

        if ans_head in ("u", "update"):
            input_id_entry = ans_tail[0] if len(ans_tail) > 0 else input("entry id:")
            try:
                id_entry = int(input_id_entry)
                update(id_entry, dao)
            except ValueError:
                "id must be int"

        if ans in ("q", "quit"):
            go_on = False

        if ans in ("init", ):
            shutil.rmtree(os.path.dirname(entrydao.db_path_default))
            dao.init_table()
