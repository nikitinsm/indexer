import struct
from collections import OrderedDict
"""
#http://docs.python.org/2/library/struct.html

Format	    C Type	                Python type	        Standard size
---------------------------------------------------------------------
x	        pad byte	            no value
c	        char	                string of length    1
b	        signed char	            integer	            1
B	        unsigned char           integer	            1
?	        _Bool	                bool	            1
h	        short	                integer	            2
H	        unsigned short	        integer	            2
i	        int	                    integer	            4
I	        unsigned int	        integer	            4
l	        long	                integer	            4
L	        unsigned long	        integer	            4
q	        long long	            integer	            8
Q	        unsigned long long	    integer	            8
f	        float	                float	            4
d	        double	                float	            8
s	        char[]	                string
p	        char[]	                string
P	        void *	                integer
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
        if name != 'BaseBlockModel':
            format = ''
            for field_name, field in attributes['_fields']:
                field.name = field_name
                attributes[field_name] = field
                field_options = field.options
                if field_options[2]:
                    format += str(field_options[2])
                format += field_options[0]
            attributes['_struct'] = struct.Struct(format)
        return type.__new__(mcs, name, bases, attributes)



class BaseBlockModel(object):
    __metaclass__ = BaseBlockModelMeta

    _fields = None
    _struct = None
    """@type: struct.Struct"""

    _data = None

    def __init__(self, *args):
        self._data = OrderedDict()
        super(BaseBlockModel, self).__init__()

        #Fill with defaults
        for field_name, field in self._fields:
            setattr(self, field_name, field.default)

        #Fill initial
        for i, initial_value in enumerate(args):
            field_name, field = self._fields[i]
            setattr(self, field_name, initial_value)

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