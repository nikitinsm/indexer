import base64
import unittest
import struct
import uuid
from indexer.base.fields import LongLongField, UuidField, IntegerField
from indexer.base.indexes import InfiniteIndex
from indexer.base.model import BaseBlockModel
from indexer.base.storage import FileStorage


class TestBase(unittest.TestCase):

    def setUp(self):

        class BlockModel(BaseBlockModel):
            _fields = \
                [ ('counter' ,  LongLongField())
                , ('next' ,     IntegerField())
                , ('prev' ,     IntegerField())
                , ('from_id' ,  UuidField())
                , ('to_id' ,    UuidField())
                ]

        self.block_class = BlockModel
        self.index = InfiniteIndex(self.block_class, FileStorage('/tmp/indexer/test.ix'))

    def test_block_consistence(self):
        block = self.block_class()

        self.assertEquals(block._struct.format, 'QII16s16s')
        self.assertEquals(len(block), 48)

        attributes =  filter(lambda v: not v.startswith('__'), dir(block))

        self.assertListEqual\
            ( ['_data', '_fields', '_struct', 'counter', 'from_id'
              , 'next', 'pack', 'prev', 'to_id', 'unpack', 'values'
              ]
            , attributes
            )

    def test_block_set_get(self):
        block = self.block_class()

        block.counter = 'test'
        self.assertListEqual(['test', 0, 0, 0, 0], block.values)
        self.assertRaises(struct.error, lambda: block.pack())

        test_uuid = uuid.UUID('01d0cd52-78e7-11e3-8585-080027f1b8ef')

        block.counter = 1
        block.next = 2
        block.prev = 3
        block.from_id = test_uuid
        block.to_id = test_uuid

        packed_data = block.pack()

        self.assertEquals\
            ( 'AQAAAAAAAAACAAAAAwAAAAHQzVJ45xHjhYUIACfxuO8B0M1SeOcR44WFCAAn8bjv\n'
            , base64.encodestring(packed_data)
            )

        self.assertEquals(test_uuid, block.to_id)

    def test_index_consistence(self):
        index = self.index

        attributes =  filter(lambda v: not v.startswith('__'), dir(index))

        self.assertEquals\
            ( ['_data', '_fields', '_struct', 'block_class', 'end_pointer'
              , 'pack', 'read_only', 'row_model', 'unpack', 'values'
              ]
            , attributes
            )









