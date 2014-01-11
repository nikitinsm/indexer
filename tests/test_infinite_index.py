import os
import random
import unittest
import uuid

from indexer.base.fields import LongLongField, UuidField, IntegerField
from indexer.base.indexes import InfiniteIndex
from indexer.base.block import BaseBlockModel
from indexer.base.storage import FileStorage



class TestIndexBase(unittest.TestCase):

    def setUp(self):
        path = '/tmp/indexer/test.ix'

        try:
            os.unlink(path)
        except OSError:
            pass

        fs = FileStorage(path)


        class BlockModel(BaseBlockModel):
            _fields = \
                [ ('counter' ,  LongLongField())
                , ('next' ,     IntegerField())
                , ('prev' ,     IntegerField())
                , ('from_id' ,  UuidField())
                , ('to_id' ,    UuidField())
                ]

        self.block_class = BlockModel
        self.index = InfiniteIndex(self.block_class, fs)

    def test_index_consistence(self):
        index = self.index

        # attributes =  filter(lambda v: not v.startswith('__'), dir(index))
        #
        # self.assertEquals\
        #     ( ['_data', '_fields', '_struct', 'append', 'block_class', 'end_pointer'
        #       , 'pack', 'read_only', 'row_model', 'unpack', 'values'
        #       ]
        #     , attributes
        #     )

    def test_index_get_set(self):
        index = self.index

        test_blocks = []

        for i in range(10):
            id = i + 1
            block = self.block_class(id, 2, 3, uuid.uuid4(), uuid.uuid4())
            index.append(block)
            test_blocks.append(block)

        r_test_block = random.choice(test_blocks)

        self.assertEqual(test_blocks[r_test_block.counter - 1], r_test_block)
        self.assertNotEqual(test_blocks[r_test_block.counter], r_test_block)


    def test_yield_index(self):
        index = self.index

        test_blocks = []

        for i in range(10):
            id = i + 1
            block = self.block_class(id, 2, 3, uuid.uuid4(), uuid.uuid4())
            index.append(block)
            test_blocks.append(block)

        result_blocks = []
        for b in index.end_iterator(10):
            result_blocks.append(b)

        test_blocks.reverse()
        for i, b2 in enumerate(test_blocks):
            self.assertListEqual(b2.values, result_blocks[i].values)




