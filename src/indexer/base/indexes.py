from indexer.base.exceptions import NotConfigured
from indexer.base.fields import IntegerField
from indexer.base.model import BaseBlockModel
from indexer.base.storage import BaseStorage


class BaseIndex(object):
    row_model = None
    read_only = None


class InfiniteIndex(BaseIndex, BaseBlockModel):
    _fields = \
        [ ('p_end', IntegerField(signed=True))
        ]

    def __init__(self, block_class, storage, read_only=False, block_offset=1024):
        test_block = block_class()

        self.block_class = block_class
        self.block_size = len(test_block)
        self.block_offset = block_offset
        self.read_only = read_only
        self.storage = storage
        """BaseStorage"""

        if not issubclass(type(storage), BaseStorage):
            raise NotConfigured('Expected BaseStorage implementation')

        super(InfiniteIndex, self).__init__()

        #load header data from DB file
        header_data = self.storage.get(len(self), 0)
        if header_data:
            self.load_bytes(header_data)

    def append(self, block):
        block_id = self.p_end + 1
        self.storage.set(block.pack(), self.block_offset + self.p_end * self.block_size)
        self.p_end += 1
        self.storage.set(self.pack(), 0)
        #self.storage.commit()

        return block_id

    def get_block(self, id):
        assert id > 0
        data = self.storage.get(self.block_size, self.block_offset + (id - 1) * self.block_size)
        return self.block_class.from_bytes(data)

    def end_iterator(self, limit):
        for bin_data in self.storage.read_from_end(self.block_size, limit):
            yield self.block_class.from_bytes(bin_data)
