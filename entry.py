import datetime


class Entry:
    def __init__(self, text="", datetime=datetime.datetime(2000, 1, 1)):
        self.text = text
        self.datetime = datetime

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, "r") as f:
            text = f.read()
            return cls(text, datetime.datetime.now())
