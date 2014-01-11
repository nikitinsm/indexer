import uuid


class BaseField(object):

    name = None
    padding = None
    options = None
    default = None

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

    def __init__(self, length=1, default=0):
        self.options = ('s', 1, length)
        self.default = default
        super(CharArrayField, self).__init__()


class IntegerField(BaseField):

    def __init__(self, signed=False, default=0):
        self.options = signed and ('i', 4, None) or ('I', 4, None)
        self.default = default
        super(IntegerField, self).__init__()


class LongLongField(BaseField):

    def __init__(self, signed=False, default=0):
        self.options = signed and ('q', 8, None) or ('Q', 8, None)
        self.default = default
        super(LongLongField, self).__init__()



class UuidField(CharArrayField):

    def __init__(self, default=None):
        super(UuidField, self).__init__(16)
        self.default = default or uuid.UUID(bytes='\0' * 16)

    @staticmethod
    def to_bytes(value):
        return value.bytes

    @staticmethod
    def from_bytes(value):
        return uuid.UUID(bytes=value)