import os
import datetime
import enum
import argparse
import tempfile
import subprocess

PREFIX = {
    "Entry": "> ",
    "Text": ". ",
}


class State(enum.Enum):
    unitialized = 0
    ongoing = 1
    ended = 2


class Base:
    def __init__(self, handler=None, state=State.unitialized):
        self.handler = handler
        self.state = state

    def process(self, line):
        if self.state is State.ended:
            raise Exception(f"{self} is ended but was called")
        return self._process(line)


class ListUnique(Base):
    def __init__(self, child_class, handler, start_symbol=None, end_symbol=None):
        super().__init__(handler)
        self.start_symbol = start_symbol
        self.end_symbol = end_symbol
        self.child_class = child_class
        self.children = []

    def _process(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
            if self.start_symbol is not None:
                pass  # do smth, return
        if self.state is State.ongoing:
            if self.end_symbol is not None:
                pass  # do smth, return
            else:
                if file_ended(line):
                    return False, None
            self.children.append(self.child_class(self))
            return False, self.children[-1]

    def __repr__(self):
        return f"<ListOnly {self.children}>"

    def __iter__(self):
        yield from self.children


class Span(Base):
    def __init__(self, prefix, collect, inital_value, handler):
        super().__init__(handler)
        self.collect = collect
        self.prefix = prefix
        self.value = inital_value

    def _process(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
        if self.state is State.ongoing:
            if line.startswith(self.prefix):
                self.value = self.collect(self.value, line[len(self.prefix):])
                return True, self
            else:
                self.state = State.ended
                return False, self.handler


class Entry(Base):
    def __init__(self, handler):
        super().__init__(handler)
        self.time = None
        self.text = Span(PREFIX["Text"], (lambda x, y: x + y), "", self)

    def _process(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
            prefix = PREFIX["Entry"]
            if line.startswith(prefix):
                self.time = datetime.datetime.fromisoformat(line[len(prefix):].strip())
            else:
                raise Exception(f"{self} expected first line to start with {prefix}")
            return True, self.text
        if self.state is State.ongoing:
            self.text = self.text.value
            self.state = State.ended
            return False, self.handler

    def __repr__(self):
        return f"<Entry {self.time}, {repr(self.text)[:32]}>"


def format_entry(date, text, pfx_entry=PREFIX["Entry"], pfx_text=PREFIX["Text"]):
    yield pfx_entry + date.isoformat()
    for line in text.split("\n"):
        yield pfx_text + line


def empty(line):
    return line.strip() == "" and line != ""  # "" is eof


def ignore(line):
    return line.startswith("//") or empty(line)


def file_ended(line):
    return line == ""


def parse_base(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    entries = ListUnique(Entry, None)
    agent = entries
    with open(file_path) as f:
        line = f.readline()
        while True:
            if ignore(line):
                line = f.readline()
                continue

            was_processed, next_agent = agent.process(line)
            if next_agent is None:
                if file_ended(line):
                    break
                else:
                    raise Exception("no next but state no ended")
            if was_processed:
                line = f.readline()
            agent = next_agent

    return entries


def get_user_input(text_in=""):
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(text_in)

        cmd = ["editor", buffer_path]
        subprocess.run(cmd)

        with open(buffer_path, "r") as f:
            text_out = f.read()
    return text_out


def new(args):
    try:
        parse_base(args.file)
    except Exception as e:
        print("Failed to parse file")
        print(e)
        exit()

    text = get_user_input()
    with open(args.file, "a") as f:
        f.write("\n".join(format_entry(datetime.datetime.now(), text)))


def read(args):
    entries = parse_base(args.file)
    for entry in entries:
        print("\n".join(format_entry(entry.time, entry.text)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_new = subparsers.add_parser("new")
    parser_new.add_argument("file")
    parser_new.set_defaults(func=new)

    parser_read = subparsers.add_parser("read")
    parser_read.set_defaults(func=read)
    parser_read.add_argument("file")

    args = parser.parse_args()

    args.func(args)
