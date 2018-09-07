from wtforms.fields import Field
from wtforms.widgets import TextInput


class TagListField(Field):
    """
    Copy-pasted from https://wtforms.readthedocs.io/en/stable/fields.html#custom-fields
    """

    widget = TextInput()

    def __init__(
        self, label="", validators=None, remove_duplicates=True, delimiter=" ", **kwargs
    ):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.delimiter = delimiter

    def _value(self):
        if self.data:
            return self.delimiter.join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [
                x.strip() for x in valuelist[0].split(self.delimiter) if bool(x.strip())
            ]
        else:
            self.data = []

        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item
