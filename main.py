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


class EntryNotFoundError(Exception):
    """ Entry not found. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


def update(id_entry, dao):
    entry_old = dao.get(id_entry)
    if entry_old is None:
        raise EntryNotFoundError()
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(entry_old.text)

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        entry_new = Entry.from_file(buffer_path)
        dao.update(id_entry, entry_new)


def delete(id_entry, dao):
    dao.delete(id_entry)


def show_text_beginning(text, max_n_char=64):
    lines = text.split("\n")
    if len(lines) <= 1:
        end = " [...]" if len(text) > max_n_char else ""
        return text[:max_n_char] + end
    else:
        return lines[0][:max_n_char] + " [...]"


if __name__ == "__main__":
    dao = entrydao.EntryDao()
    go_on = True
    print("n/u/d/l/q")
    while go_on:
        ans = input()
        ans_splitted = ans.split()
        ans_head = ans_splitted[0] if len(ans_splitted) > 0 else None
        ans_tail = ans_splitted[1:]
        if ans in ("n", "new", "w", "write"):
            write_new(dao)

        if ans in ("l", "list"):
            for id, entry in dao.get_all():
                print(f"{id}.", show_text_beginning(entry.text.strip()))

        if ans_head in ("u", "update"):
            input_id_entry = ans_tail[0] if len(ans_tail) > 0 else input("entry id:")
            try:
                id_entry = int(input_id_entry)
            except ValueError:
                print("id must be int")
            else:
                try:
                    update(id_entry, dao)
                except EntryNotFoundError:
                    print(f"Entry with id {id_entry} not found")

        if ans_head in ("d", "del", "delete"):
            input_id_entry = ans_tail[0] if len(ans_tail) > 0 else input("entry id:")
            try:
                id_entry = int(input_id_entry)
                nb_row_deleted = dao.delete(id_entry)
                if nb_row_deleted == 0:
                    print("no row deleted")
            except ValueError:
                print("id must be int")

        if ans in ("q", "quit"):
            go_on = False

        if ans in ("init",):
            shutil.rmtree(os.path.dirname(entrydao.db_path_default))
            dao.init_table()
