import datetime as dt


class Entry:
    def __init__(self, text="", creation_datetime=None, update_datetime=None, topic=None):
        self.text = text
        self.creation_datetime = creation_datetime if creation_datetime is not None else dt.datetime.now()
        self.update_datetime = update_datetime if update_datetime is not None else self.creation_datetime
        self.topic = topic

    def update(self, text=None, topic=None):
        """returns a new entry with same creation_dt, now() as update_dt and other fields updated according to given args"""
        return type(self)(
                creation_datetime = self.creation_datetime,
                update_datetime = dt.datetime.now(),
                text = self.text if text is None else text,
                topic = self.topic if topic is None else topic
                )


class EntryNotFoundError(Exception):
    """ Entry not found. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
