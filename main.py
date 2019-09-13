import cmd
import os
import random
import shutil
import signal
import string
import subprocess
import tempfile

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


def show_text_beginning(text, max_n_char=32, going_on="..."):
    cut = text[:max_n_char + 1].replace("\n", " ")
    end = going_on if len(cut) > max_n_char else ""
    s = cut[:max_n_char - len(end)] + end
    return f"{s:<{max_n_char}}"


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


def list_entries(dao):
    for id, entry in dao.get_all():
        print(f"{id}|", show_text_beginning(entry.text.strip()), datetime_str_default(entry.datetime), f"|{id}")


def show(dao, id_entry):
    entry = dao.get(id_entry)
    if entry is not None:
        n = max([len(line) for line in entry.text.split("\n")])
        print("=" * n)
        print(entry.text.strip())
        print("=" * n)
    else:
        print(f"Entry with id {id_entry} not found")


def delete(dao, id_entry):
    nb_row_deleted = dao.delete(id_entry)
    print(f"nb of rows deleted: {nb_row_deleted}")


def reset(dao):
    shutil.rmtree(os.path.dirname(entrydao.db_path_default))
    dao.init_table()


def help(actions):
    print("/".join([sorted(aliases, key=len)[0] for action, aliases in actions.items()]))


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
        list_entries(self.dao)

    @check_arg_id_entry
    def do_show(self, arg):
        show(self.dao, arg)

    @check_arg_id_entry
    def do_update(self, arg):
        update(self.dao, arg)

    def do_new(self, arg):
        write_new(self.dao)

    def do_random(self, arg):
        write_random_entry(self.dao)

    @prompt_warning
    @check_arg_id_entry
    def do_delete(self, arg):
        delete(self.dao, arg)

    @prompt_warning
    def do_reset(self, arg):
        reset(self.dao)

    def do_EOF(self, arg):
        print("Bye")
        return True

    def do_quit(self, arg):
        return self.do_EOF(arg)


def exit_handler(sig, frame):
    print("\nBye")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)

    MainCmd(entrydao.EntryDao()).cmdloop()
