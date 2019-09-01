import os
import shutil
import subprocess
from entry import Entry, EntryNotFoundError
import entrydao
import tempfile

DEFAULT_HEADER_SIZE = 2


def datetime_str_default(datetime):
    return f"({datetime:%Y-%m-%d:%H.%M})"


def get_user_input(text_in=""):
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(text_in)

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        with open(buffer_path, "r") as f:
            text_out = f.read()
    return text_out


def entry_from_user_input(text, header_size=DEFAULT_HEADER_SIZE):
    """header lines are ignored """
    lines = text.split("\n")
    new_text = "\n".join(lines[header_size:])
    return Entry(new_text)


def make_header(creation_datetime):
    datetime_str = datetime_str_default(creation_datetime)
    line = f"created: {datetime_str}"
    bar = "~" * len(line)
    return f"{line}\n{bar}"


def entry_to_user_input(entry):
    template = "{header}\n{body}"
    return template.format(body=entry.text, header=make_header(entry.datetime))


def show_text_beginning(text, max_n_char=64):
    lines = text.split("\n")
    if len(lines) <= 1:
        end = " [...]" if len(text) > max_n_char else ""
        return text[:max_n_char] + end
    else:
        return lines[0][:max_n_char] + " [...]"


def write_new(dao):
    entry_new = entry_from_user_input(get_user_input())
    dao.write(entry_new)


def update(id_entry, dao):
    entry_old = dao.get(id_entry)
    if entry_old is None:
        raise EntryNotFoundError()
    entry_new = entry_from_user_input(get_user_input(entry_to_user_input(entry_old)))
    dao.update(id_entry, entry_new)


def list_entries():
    for id, entry in dao.get_all():
        print(f"{id}.", datetime_str_default(entry.datetime), show_text_beginning(entry.text.strip()))


def show(id_entry):
    entry = dao.get(id_entry)
    if entry is not None:
        n = max([len(line) for line in entry.text.split("\n")])
        print("=" * n)
        print(entry.text.strip())
        print("=" * n)
    else:
        print(f"Entry with id {id_entry} not found")


def delete(id_entry, dao):
    dao.delete(id_entry)


def reset():
    shutil.rmtree(os.path.dirname(entrydao.db_path_default))
    dao.init_table()


def help():
    print("h/l/s/n/u/d/q/reset")


if __name__ == "__main__":
    dao = entrydao.EntryDao()
    go_on = True
    help()
    while go_on:
        ans = input()
        ans_splitted = ans.split()
        ans_head = ans_splitted[0] if len(ans_splitted) > 0 else None
        ans_tail = ans_splitted[1:]

        if ans in ("h", "help"):
            help()

        if ans in ("n", "new", "w", "write"):
            write_new(dao)

        if ans in ("l", "list"):
            print(".")
            list_entries()

        if ans_head in ("s", "show"):
            input_id_entry = ans_tail[0] if len(ans_tail) > 0 else input("entry id:")
            try:
                id_entry = int(input_id_entry)
            except ValueError:
                print("id must be int")
            else:
                show(id_entry)

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
            except ValueError:
                print("id must be int")
            else:
                nb_row_deleted = 0
                if input(f"delete entry {id_entry} (y/*) ?") == "y":
                    nb_row_deleted = dao.delete(id_entry)
                print("no row deleted" if nb_row_deleted < 1
                      else f"deleted {nb_row_deleted} row" + "s" * (nb_row_deleted > 1))

        if ans in ("reset",):
            if input("reset the table? (y/*)") == "y":
                reset()

        if ans in ("q", "quit"):
            go_on = False
