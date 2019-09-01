import os
import shutil
import subprocess
from entry import Entry, EntryNotFoundError
import entrydao
import tempfile
import random
import string

DEFAULT_HEADER_SIZE = 2


def force_arg_to_int(n_arg=0):
    def force_arg_to_int_decorator(func):
        def func_wrapper(*args, **kwargs):
            if n_arg >= len(args):
                raise ValueError(f"Asked to check arg {n_arg} but got only {len(args)} args")
            args_list = list(args)
            try:
                args_list[n_arg] = int(args_list[n_arg])
            except ValueError:
                print(f"Expected argument to be int or to be convertible to int, unlike: {args_list[n_arg]}")
            else:
                return func(*args_list, **kwargs)

        return func_wrapper

    return force_arg_to_int_decorator


def double_check(s="Sure?"):
    def double_check_decorator(func):
        def func_wrapper(*args, **kwargs):
            if input(f"{s} (y/*)") == "y":
                func(*args, **kwargs)
            else:
                print("nothing happened")

        return func_wrapper

    return double_check_decorator


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


@force_arg_to_int()
def update(id_entry, dao):
    entry_old = dao.get(id_entry)
    if entry_old is None:
        print(f"Entry with id {id_entry} not found")
        return
    entry_new = entry_from_user_input(get_user_input(entry_to_user_input(entry_old)))
    dao.update(id_entry, entry_new)


def list_entries(dao):
    for id, entry in dao.get_all():
        print(f"{id}|", show_text_beginning(entry.text.strip()), datetime_str_default(entry.datetime), f"|{id}")


@force_arg_to_int()
def show(id_entry, dao):
    entry = dao.get(id_entry)
    if entry is not None:
        n = max([len(line) for line in entry.text.split("\n")])
        print("=" * n)
        print(entry.text.strip())
        print("=" * n)
    else:
        print(f"Entry with id {id_entry} not found")


@double_check("Sure to delete?")
@force_arg_to_int()
def delete(input_id_entry, dao):
    nb_row_deleted = dao.delete(input_id_entry)
    print(f"nb of rows deleted: {nb_row_deleted}")


@double_check("Sure to reset?")
def reset():
    shutil.rmtree(os.path.dirname(entrydao.db_path_default))
    dao.init_table()


def help():
    print("h/l/s/n/u/d/q/reset/random")


def write_random_entry(dao, text_size=64):
    chars = " " + string.ascii_lowercase
    text = "".join(random.choices(chars, weights=[8] + [1 for _ in string.ascii_lowercase], k=text_size))
    dao.write(Entry(text))


if __name__ == "__main__":

    def get_entry_id_or_ask(ans_tail):
        return ans_tail[0] if len(ans_tail) > 0 else input("entry id?")

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
            list_entries(dao)

        if ans_head in ("s", "show"):
            show(get_entry_id_or_ask(ans_tail), dao)

        if ans_head in ("u", "update"):
            update(get_entry_id_or_ask(ans_tail), dao)

        if ans_head in ("d", "del", "delete"):
            delete(get_entry_id_or_ask(ans_tail), dao)

        if ans in ("reset",):
            reset()

        if ans in ("random",):
            write_random_entry(dao)

        if ans in ("q", "quit"):
            go_on = False
