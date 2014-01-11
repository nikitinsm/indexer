import os
import profile
import resource
import time
import unittest
import random
import mysql

from collections import namedtuple
from indexer.base import uuid_generator
from indexer.base.block import BaseBlockModel
from indexer.base.fields import LongLongField, UuidField
from indexer.base.indexes import InfiniteIndex
from indexer.base.storage import FileStorage


class TestEventBase(unittest.TestCase):

    def setUp(self):
        path = '/tmp/indexer/test_event.ix'

        try:
            os.unlink(path)
        except OSError:
            pass

        fs = FileStorage(path)

        class BlockModel(BaseBlockModel):
            _fields = \
                [ ('created',  LongLongField())
                , ('user_id',  UuidField())
                , ('post_id',  UuidField())
                ]

        self.block_class = BlockModel
        self.index = InfiniteIndex(self.block_class, fs)

        try:
            uuid_generator.register('user', 1)
        except Exception as e:
            pass

        try:
            uuid_generator.register('post', 2)
        except Exception as e:
            pass


    def create_uuids(self, num=1000, node='user', bytes=False):
        result = []
        for i in xrange(num):
            result.append(uuid_generator.create(node).bytes)
        return result


    def create_index(self, users=10000, posts=100000):
        users = self.create_uuids(num=users, node='user')

        index = self.index

        created_initial = int(round(time.time() * 1000))

        for i in xrange(posts):
            choosed_user = random.choice(users)
            index.append(self.block_class(created_initial + i, choosed_user, uuid_generator.create('post')))
        index.storage.commit()

        return users, created_initial, created_initial + posts

    def create_index2(self, users=10000, posts=10 ** 6):
        Block = namedtuple('Block', 'created user_id post_id')
        users = self.create_uuids(num=users, node='user', bytes=True)
        result = []
        created_initial = int(round(time.time() * 1000))
        for i in xrange(posts):
            choosed_user = random.choice(users)
            result.append( Block( created=created_initial + 1
                                , user_id=choosed_user
                                , post_id=uuid_generator.create('post').bytes
                                ) )
        return users, result

    def _test_test_memory(self):
        users, index = self.create_index2()

        users_to_find = []
        for i in xrange(500):
            users_to_find.append(random.choice(users))


        def search():
            count = 0
            scanned = 0
            start_time = time.time()
            for i, item in enumerate(reversed(index)):
                scanned += 1
                if item.user_id in users_to_find:
                    memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                    print scanned, '%dM' % memory_usage, item
                    count += 1
                    if count > 9:
                        break
            print '%.6f' % (time.time() - start_time)

        # p = profile.Profile()
        # p.runcall(search)
        # p.print_stats()

        search()


    def test_test_mysql(self):
        mysql.connector.connect(user='uwsgi', database='nasimke_test')





    def _test_base(self):
        users, created_initial, created_destination = self.create_index()

        #assert size
        #self.assertEqual(401024, os.fstat(self.index.storage.handler.fileno()).st_size)

        #get 10 users to find posts
        users_to_find = []
        for i in xrange(500):
            users_to_find.append(random.choice(users))

        i = 0
        start_time = time.time()
        for b in self.index.end_iterator(10000):
            if i > 10:
                break
            user_id = b.user_id
            if user_id in users_to_find:
                print user_id
                i += 1
        print '%.6f' % (time.time() - start_time)

    def _test_test1(self):
        users, created_initial, created_destination = self.create_index()

        #get 10 users to find posts
        users_to_find = []
        for i in xrange(100):
            users_to_find.append(random.choice(users).bytes)

        def search():
            for skanned, b in self.index.storage.find_from_end(self.index.block_size, 8, 16, users_to_find, 10):
                print skanned#, self.index.block_class.from_bytes(b).values

        p = profile.Profile()
        p.runcall(search)
        p.print_stats()