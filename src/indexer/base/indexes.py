import os
from indexer.base.exceptions import NotConfigured
from indexer.base.fields import IntegerField
from indexer.base.model import BaseBlockModel


class BaseIndex(object):
    row_model = None
    read_only = None



class InfiniteIndex(BaseIndex, BaseBlockModel):
    _fields = \
        [ ('end_pointer', IntegerField(signed=True))
        ]

    def __init__(self, block_class, path=None, read_only=False):
        self.block_class = block_class
        self.read_only = read_only

        if not path:
            raise NotConfigured('expected index storage path')

        super(InfiniteIndex, self).__init__()