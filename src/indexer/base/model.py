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

    def __init__(self, **kwargs):
        self._data = OrderedDict()
        for field_name, field in self._fields:
            self._data[field_name] = kwargs.get(field_name, 0)
        super(BaseBlockModel, self).__init__()

    def __len__(self):
        return self._struct.size

    @property
    def values(self):
        return self._data.values()

    def pack(self, *values):
        return self._struct.pack(*(values or self.values))

    def unpack(self, data):
        return self._struct.unpack(data)
