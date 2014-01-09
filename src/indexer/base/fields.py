import uuid


class BaseField(object):

    name = None
    padding = None
    options = None

    def __set__(self, instance, value):
        instance._data[self.name] = self.to_bytes(value)

    def __get__(self, instance, owner):
        result = instance._data.get(self.name, None)
        return result and self.from_bytes(result) or result

    @staticmethod
    def to_bytes(value):
        return value

    @staticmethod
    def from_bytes(value):
        return value


class CharArrayField(BaseField):

    def __init__(self, length=1):
        self.options = ('s', 1, length)
        super(CharArrayField, self).__init__()


class IntegerField(BaseField):

    def __init__(self, signed=False):
        self.options = signed and ('i', 4, None) or ('I', 4, None)
        super(IntegerField, self).__init__()


class LongLongField(BaseField):

    def __init__(self, signed=False):
        self.options = signed and ('q', 8, None) or ('Q', 8, None)
        super(LongLongField, self).__init__()



class UuidField(CharArrayField):

    def __init__(self):
        super(UuidField, self).__init__(16)

    @staticmethod
    def to_bytes(value):
        return value.bytes

    @staticmethod
    def from_bytes(value):
        return uuid.UUID(bytes=value)