import cmd
import os
import random
import shutil
import signal
import string
import subprocess
import tempfile
import datetime
import dbmigrations.migrations

import entrydao
from entry import Entry

DEFAULT_HEADER_SIZE = 2


def prompt_warning(func):
    def wrapper(*args, **kwargs):
        if you_sure():
            func(*args, **kwargs)
    return wrapper


def you_sure():
    if input("Are you sure? (Y/*) ").lower() in ("", "y", "yes"):
        return True
    print("nothing happened")
    return False


def check_arg_id_entry(func):
    def wrapper(self, arg):
        try:
            id_entry = get_check_id_entry(arg)
            func(self, id_entry)
        except Exception as e:
            print(e)
    return wrapper


def datetime_str_default(datetime):
    return f"({datetime:%Y-%m-%d:%H.%M})"


def get_user_input(text_entry):
    text, entry = text_entry
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(text)

        cmd = ["vim", buffer_path]
        subprocess.run(cmd)

        with open(buffer_path, "r") as f:
            text_out = f.read()
    return text_out, entry


def entry_from_user_input(text_entry, header_size=DEFAULT_HEADER_SIZE):
    """header lines are ignored """
    text, entry = text_entry
    lines = text.split("\n")
    new_text = "\n".join(lines[header_size:])
    return entry.update(text=new_text)


def make_header(entry):
    datetime_str = datetime_str_default(entry.creation_datetime)
    line = f"created: {datetime_str} | topic: {entry.topic}"
    bar = "~" * len(line)
    return f"{line}\n{bar}"


def entry_to_user_input(entry):
    template = "{header}\n{body}"
    return template.format(body=entry.text, header=make_header(entry)), entry


def _text_beginning(text, max_n_char=32, going_on="..."):
    cut = text[:max_n_char + 1].replace("\n", " ")
    end = going_on if len(cut) > max_n_char else ""
    s = cut[:max_n_char - len(end)] + end
    return f"{s:<{max_n_char}}"


def display_ids_entries(ids_entries):
    for id, entry in ids_entries:
        print(f"{id}|",
              _text_beginning(entry.text.strip()),
              datetime_str_default(entry.creation_datetime),
              datetime_str_default(entry.update_datetime),
              entry.topic,
              f"|{id}")


def write_new(dao):
    entry_new = entry_from_user_input(get_user_input(entry_to_user_input(Entry())))
    dao.write(entry_new)


def update(dao, id_entry):
    entry_old = dao.get(id_entry)
    if entry_old is None:
        print(f"Entry with id {id_entry} not found")
        return
    entry_new = entry_from_user_input(get_user_input(entry_to_user_input(entry_old)))
    dao.update(id_entry, entry_new)


def list_all(dao):
    display_ids_entries(dao.get_all())


def simple_search(dao, s):
    display_ids_entries(dao.get_containing(s))


def view(dao, id_entry):
    entry = dao.get(id_entry)
    if entry is not None:
        n = max([len(line) for line in entry.text.split("\n")])
        print("=" * n)
        print(entry.text.strip())
        print("=" * n)
    else:
        print(f"Entry with id {id_entry} not found")

def set_topic(dao, id_entry):
    entry = dao.get(id_entry)
    if entry is not None:
        print(f"Actual topic is {entry.topic}")
        new_topic = input("New topic: ")
        dao.update(id_entry, entry.update(topic=new_topic))
    else:
        print(f"Entry with id {id_entry} not found")


def delete(dao, id_entry):
    nb_row_deleted = dao.delete(id_entry)
    print(f"nb of rows deleted: {nb_row_deleted}")


def reset(dao):
    shutil.rmtree(os.path.dirname(entrydao.db_path_default))
    migrate(dao)


def migrate(dao):
    dbmigrations.migrations.do_migrations(dao.db_path)


def write_random_entry(dao, text_size=64):
    chars = " " + string.ascii_lowercase
    text = "".join(random.choices(chars, weights=[8] + [1 for _ in string.ascii_lowercase], k=text_size))
    dao.write(Entry(text))


def get_check_id_entry(ans_tail):
    input_entry = ans_tail if len(ans_tail) > 0 else input("entry id? ")
    try:
        return int(input_entry)
    except ValueError:
        raise ValueError(f"Expected integer, unlike: {input_entry}")


class MainCmd(cmd.Cmd):
    def __init__(self, dao):
        super().__init__()
        self.dao = dao
        self.prompt = "(aov) "

    def do_list(self, arg):
        list_all(self.dao)

    def do_search(self, arg):
        simple_search(self.dao, arg)

    @check_arg_id_entry
    def do_view(self, arg):
        view(self.dao, arg)

    @check_arg_id_entry
    def do_update(self, arg):
        update(self.dao, arg)

    def do_new(self, arg):
        write_new(self.dao)

    def do_random(self, arg):
        write_random_entry(self.dao)

    @check_arg_id_entry
    def do_topic(self, arg):
        set_topic(self.dao, arg)

    @prompt_warning
    @check_arg_id_entry
    def do_delete(self, arg):
        delete(self.dao, arg)

    @prompt_warning
    def do_reset(self, arg):
        reset(self.dao)

    @prompt_warning
    def do_migrate(self, arg):
        migrate(self.dao)

    def do_EOF(self, arg):
        print("Bye")
        return True

    def do_quit(self, arg):
        return self.do_EOF(arg)

    def precmd(self, line):
        # allow to call a command with its first letter, when no ambiguity
        args = line.split()
        names = [name[3:] for name in self.get_names() if name.startswith("do_")]
        if args and len(args[0]) == 1:
            c = args[0]
            matching_names = list(filter(lambda s: s.startswith(c), names))
            if len(matching_names) == 1:
                line = matching_names[0] + line[1:]
        return line


def exit_handler(sig, frame):
    print("\nBye")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)

    MainCmd(entrydao.EntryDao()).cmdloop()
