import datetime as dt


class Entry:
    def __init__(self, text="", datetime=None):
        self.text = text
        self.datetime = datetime if datetime is not None else dt.datetime.now()


class EntryNotFoundError(Exception):

    """ Entry not found. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
