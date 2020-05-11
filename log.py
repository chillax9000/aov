import os
import datetime
import enum

PREFIX = {
    "Entry": "> ",
    "Text": ". ",
}


class State(enum.Enum):
    unitialized = 1
    ongoing = 2

    ended = -1
    error = -2

    def __bool__(self):
        return bool(self.value)


class ListUnique:
    def __init__(self, child_class, handler, start_symbol=None, end_symbol=None):
        self.handler = handler
        self.state = State.unitialized
        self.start_symbol = start_symbol
        self.end_symbol = end_symbol
        self.child_class = child_class
        self.children = []

    def deal_with(self, line):
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

        raise Exception(f"{self} is ended but was called")

    def __repr__(self):
        return f"<ListOnly {self.children}>"


class Span:
    def __init__(self, prefix, collect, inital_value, handler):
        self.handler = handler
        self.state = State.unitialized
        self.collect = collect
        self.prefix = prefix
        self.value = inital_value

    def deal_with(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
        if self.state is State.ongoing:
            if line.startswith(self.prefix):
                self.value = self.collect(self.value, line[len(self.prefix):])
                return True, self
            else:
                self.state = State.ended
                return False, self.handler

        raise Exception(f"{self} is ended but was called")


class Entry:
    def __init__(self, handler):
        self.handler = handler
        self.state = State.unitialized
        self.time = None
        self.text = Span(PREFIX["Text"], (lambda x, y: x + y), "", self)

    def deal_with(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
            prefix = PREFIX["Entry"]
            if line.startswith(prefix):
                self.time = datetime.datetime.fromisoformat(line[len(prefix):].strip())
            else:
                raise Exception(f"{self} expected first line to start with {prefix}")
            return True, self.text
        if self.state is State.ongoing:
            self.state = State.ended
            return False, self.handler

        raise Exception(f"{self} is ended but was called")

    def __repr__(self):
        return f"<Entry {self.time}, {repr(self.text.value[:32])}>"


def empty(line):
    return line.strip() == "" and line != ""  # "" is eof


def ignore(line):
    return line.startswith("//") or empty(line)


def file_ended(line):
    return line == ""


def parse_base(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    entries = ListUnique(Entry, None)
    agent = entries
    with open(file_path) as f:
        line = f.readline()
        while True:
            if ignore(line):
                line = f.readline()
                continue

            was_processed, next_agent = agent.deal_with(line)
            if next_agent is None:
                if file_ended(line):
                    break
                else:
                    raise Exception("no next but state no ended")
            if was_processed:
                line = f.readline()
            agent = next_agent

    return entries


if __name__ == "__main__":
    print(parse_base("log_test"))
