import os
import datetime
import enum

PREFIX = {
    "Text": ". ",
    "Entry": "> ",
}


class State(enum.Enum):
    unitialized = 1
    ongoing = 2

    ended = -1
    error = -2
    eof = -3

    def __bool__(self):
        return bool(self.value)


class Entry:
    def __init__(self, handler):
        self.handler = handler
        self.state = State.unitialized
        self.time = None
        self.text = Span(PREFIX["Text"], (lambda x, y: x + y), "", self)

    def deal_with(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
            if line.startswith(PREFIX["Entry"]):
                self.time = datetime.datetime.fromisoformat(line[2:].strip())
            else:
                raise ValueError(f"{self} expected first line to start with {PREFIX['entry']}")
            return True, self.text
        if self.state is State.ongoing:
            self.state = State.ended
            return False, self.handler

        return False, None

    def __repr__(self):
        return f"<Entry {self.time}, {self.text.value[:32]}>"


class Span:
    def __init__(self, symbol, collect, initial, handler):
        self.handler = handler
        self.state = State.unitialized
        self.collect = collect
        self.symbol = symbol
        self.value = initial

    def deal_with(self, line):
        if self.state is State.unitialized:
            self.state = State.ongoing
        if self.state is State.ongoing:
            if line.startswith(self.symbol):
                self.value = self.collect(self.value, line[2:].replace("\n", " "))
                return True, self
            else:
                self.state = State.ended
                return False, self.handler

        return False, None


def empty(line):
    return line.strip() == "" and line != ""  # "" is eof


def ignore(line):
    return line.startswith("//") or empty(line)


def file_ended(line):
    return line == ""


def parse_base(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    entries = []
    with open(file_path) as f:
        agent = Entry(None)
        line = f.readline()
        while True:
            if ignore(line):
                line = f.readline()
                continue

            was_processed, next_agent = agent.deal_with(line)
            if next_agent is None:
                if agent.state is State.ended:
                    entries.append(agent)
                    if file_ended(line):
                        break
                    else:
                        next_agent = Entry(None)
                else:
                    raise ValueError("no next but state no ended")

            if was_processed:
                line = f.readline()
            agent = next_agent

    return entries


if __name__ == "__main__":
    print(parse_base("log_test"))
