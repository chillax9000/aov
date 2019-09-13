import datetime as dt


class Entry:
    def __init__(self, text="", creation_datetime=None, update_datetime=None):
        self.text = text
        self.creation_datetime = creation_datetime if creation_datetime is not None else dt.datetime.now()
        self.update_datetime = update_datetime if update_datetime is not None else self.creation_datetime


class EntryNotFoundError(Exception):
    """ Entry not found. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
