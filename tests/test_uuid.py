import unittest
from indexer.base import uuid_generator
from indexer.base.uuid_generator import uuid_to_dt


class TestUuidBase(unittest.TestCase):

    def setUp(self):
        try:
            uuid_generator.register('user', 1)
        except Exception as e:
            pass

    def test_register(self):
        self.assertEquals(uuid_generator.node('user'), 1)
        self.assertEquals(uuid_generator.node(1), 1)

        def register_repeated():
            uuid_generator.register('test', 1)

        self.assertRaises(Exception, register_repeated)

        uuid_generator.register('post', 2)

    def test_create(self):
        u = uuid_generator.create('user')
        self.assertEqual(u.node, 1)

    def test_datetime(self):
        u = uuid_generator.create('user')
        print uuid_to_dt(u)