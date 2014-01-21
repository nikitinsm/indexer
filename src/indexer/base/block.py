import struct
from collections import OrderedDict
"""
#http://docs.python.org/2/library/struct.html

Format      C Type                  Python type         Standard size
---------------------------------------------------------------------
x           pad byte                no value
c           char                    string of length    1
b           signed char             integer             1
B           unsigned char           integer             1
?           _Bool                   bool                1
h           short                   nteger              2
H           unsigned short          integer             2
i           int                     integer             4
I           unsigned int            integer             4
l           long                    integer             4
L           unsigned long           integer             4
q           long long               integer             8
Q           unsigned long long      integer             8
f           float                   float               4
d           double                  float               8
s           char[]                  string
p           char[]                  string
P           void *                  integer
---------------------------------------------------------------------
"""


STRUCT_TYPES = \
    { 'char':                   ('c', 1)
    , 'char[]':                 ('s', None)
    , 'unsigned char':          ('B', 1)
    , 'unsigned int':           ('I', 4)
    , 'unsigned long long':     ('Q', 8)
    }


class BaseBlockModelMeta(type):

    def __new__(mcs, name, bases, attributes):
        result = type.__new__(mcs, name, bases, attributes)
        if getattr(result, '_fields', None):
            format = ''
            padding = 0
            setattr(result, '_fields_by_name', dict())
            for field_name, field in result._fields:
                field_options = field.options
                field.name = field_name

                setattr(result, field_name, field)

                result._fields_by_name[field_name] = field

                #set padding by format
                if format:
                    padding = struct.Struct(format).size
                field.padding = padding

                #render format
                if field_options[2]:
                    format += str(field_options[2])
                format += field_options[0]
            result._struct = struct.Struct(format)
        return result




class BaseBlockModel(object):
    __metaclass__ = BaseBlockModelMeta

    _fields = None
    _fields_by_name = None
    _struct = None
    """@type: struct.Struct"""

    _data = None

    def __init__(self, *args, **kwargs):
        bytes = kwargs.get('_bytes', False)
        self._data = OrderedDict()
        super(BaseBlockModel, self).__init__()

        #Fill with defaults
        for field_name, field in self._fields:
            setattr(self, field_name, field.default)

        #Fill initial
        if not bytes:
            for i, initial_value in enumerate(args):
                field_name, field = self._fields[i]
                setattr(self, field_name, initial_value)
        else:
            for i, initial_value in enumerate(args):
                field_name, field = self._fields[i]
                self._data[field_name] = initial_value

    def __len__(self):
        return self._struct.size

    def __eq__(self, other):
        return self.values == other.values

    @property
    def values(self):
        return self._data.values()

    def pack(self, *values):
        return self._struct.pack(*(values or self.values))

    @classmethod
    def unpack(cls, data):
        return cls._struct.unpack(data)

    @classmethod
    def from_bytes(cls, bin_data):
        result = cls()
        result.load_bytes(bin_data)
        return result

    def load_bytes(self, bin_data):
        data = self.unpack(bin_data)
        for i, value in enumerate(data):
            field_name, field = self._fields[i]
            self._data[field_name] = value

    def get_field(self, name):
        return self._fields_by_name[name]