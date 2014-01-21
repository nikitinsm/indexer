import os
import profile
import time
import unittest
import random
import blist

from indexer.base import uuid_generator
from indexer.base.storage import FileStorage
from indexer.generic import SocialEventList


class TestSocialEventList(unittest.TestCase):

    def setUp(self):
        path = '/tmp/indexer/test_event_generic.ix'

        try:
            os.unlink(path)
        except OSError:
            pass

        fs = FileStorage(path)

        self.index = SocialEventList(storage=fs)

        try:
            uuid_generator.register('user', 1)
        except Exception as e:
            pass

        try:
            uuid_generator.register('post', 2)
        except Exception as e:
            pass


    def test_padding(self):
        block_data = uuid_generator.create('user'), uuid_generator.create('post'), 1, 0, 0, '\0'
        block = self.index.block_class(*block_data)

        paddings = \
            [ block._fields_by_name['user_id'].padding
            , block._fields_by_name['post_id'].padding
            , block._fields_by_name['id'].padding
            , block._fields_by_name['prev_p'].padding
            , block._fields_by_name['next_p'].padding
            , block._fields_by_name['skip'].padding
            ]

        self.assertListEqual([0, 16, 32, 36, 40, 44], paddings)
        self.assertEqual(45, len(block))

    def test_base(self):
        block = uuid_generator.create('user'), uuid_generator.create('post'), 0
        block_id = self.index.append(*block)

        find_block = self.index.get_block(block_id)

        self.assertEqual(find_block.user_id, block[0])
        self.assertEqual(find_block.post_id, block[1])

    def create_uuids(self, num=1000, node='user', bytes=False):
        result = []
        for i in xrange(num):
            result.append(bytes and uuid_generator.create(node).bytes or uuid_generator.create(node))
        return result

    def create_index(self, block_num=1000, user_num=10):
        users = dict()
        for user_id in self.create_uuids(user_num, bytes=True):
            users[user_id] = 0

        for i in xrange(block_num):
            choosed_user = random.choice(users.keys())
            block = choosed_user, uuid_generator.create('post').bytes, users[choosed_user]
            block_id = self.index.append(*block, bytes=True)
            users[choosed_user] = block_id

        return users

    def test_by_back_ref(self):
        entries = 1000
        users = 10
        self.create_index(entries, users)

        item = item_initial = self.index.end_iterator(1).next()

        scans = 0
        while item.prev_p:
            scans += 1
            item = self.index.get_block(item.prev_p)
            self.assertEqual(item_initial.user_id, item.user_id)
            self.assertNotEqual(item_initial.id, item.id)

        self.assertLess(scans, 1000)

    def _test_by_back_ref_performance_1(self):
        entries = 10000
        users = 10
        self.create_index(entries, users)

        def do():
            item = self.index.end_iterator(1).next()
            scans = 0
            start_time = time.time()
            while item.prev_p:
                scans += 1
                item = self.index.get_block(item.prev_p)
            print 'scans: %d' % scans
            print '%.6f' % (time.time() - start_time)

        p = profile.Profile()
        p.runcall(do)
        p.print_stats()

    def test_consistence(self):
        entries = 1000
        users = 10
        self.create_index(entries, users)

        check_user = None
        item_prev_prev_p = None

        for item in self.index.end_iterator(1):
            # if item.prev_p:
            #     print item
            # print item.prev_p
            if not check_user:
                check_user = item.user_id

            if item.user_id == check_user:
                # print item.id, item.user_id, item.prev_p
                if item_prev_prev_p is not None:
                    self.assertEqual(item_prev_prev_p, item.id)
                item_prev_prev_p = item.prev_p

        self.assertNotEqual(item_prev_prev_p, None)

    def test_by_search_list_algo(self):
        u1 = uuid_generator.create('user').bytes
        u2 = uuid_generator.create('user').bytes
        u3 = uuid_generator.create('user').bytes

        p1 = uuid_generator.create('post').bytes
        p2 = uuid_generator.create('post').bytes
        p3 = uuid_generator.create('post').bytes
        p4 = uuid_generator.create('post').bytes
        p5 = uuid_generator.create('post').bytes
        p6 = uuid_generator.create('post').bytes
        p7 = uuid_generator.create('post').bytes
        p8 = uuid_generator.create('post').bytes
        p9 = uuid_generator.create('post').bytes

        self.index.append(u1, p1, 0, bytes=True)
        self.index.append(u2, p2, 0, bytes=True)
        self.index.append(u3, p3, 0, bytes=True)
        self.index.append(u1, p4, 1, bytes=True)
        self.index.append(u2, p5, 2, bytes=True)
        self.index.append(u3, p6, 3, bytes=True)
        self.index.append(u3, p7, 6, bytes=True)
        self.index.append(u2, p8, 5, bytes=True)
        self.index.append(u2, p9, 8, bytes=True)

        user_last_post = \
            [ [u1, 4]
            , [u2, 9]
            , [u3, 7]
            ]

        user_last_post.sort(key=lambda v: v[1], reverse=True)
        user_last_post_len = len(user_last_post)

        result = list()

        while user_last_post_len:
            b = self.index.get_block(user_last_post[0][1])
            result.append(b.id)

            if not b.prev_p:
                del user_last_post[0]
                user_last_post_len -= 1
                continue

            user_last_post[0][1] = b.prev_p
            if user_last_post_len > 1 and b.prev_p < user_last_post[1][1]:
                user_last_post.sort(key=lambda v: v[1], reverse=True)


        self.assertListEqual([9, 8, 7, 6, 5, 4, 3, 2, 1], result)

    def test_sorting_dict(self):
        d = dict()
        keys = range(10000)

        while keys:
            choice = random.choice(keys)
            d[choice] = uuid_generator.create('user')
            keys.remove(choice)

        self.assertListEqual(d.keys(), sorted(range(10000)))

    def test_by_search_sortedblist_algo(self):
        u1 = uuid_generator.create('user').bytes
        u2 = uuid_generator.create('user').bytes
        u3 = uuid_generator.create('user').bytes

        p1 = uuid_generator.create('post').bytes
        p2 = uuid_generator.create('post').bytes
        p3 = uuid_generator.create('post').bytes
        p4 = uuid_generator.create('post').bytes
        p5 = uuid_generator.create('post').bytes
        p6 = uuid_generator.create('post').bytes
        p7 = uuid_generator.create('post').bytes
        p8 = uuid_generator.create('post').bytes
        p9 = uuid_generator.create('post').bytes

        self.index.append(u1, p1, 0, bytes=True)
        self.index.append(u2, p2, 0, bytes=True)
        self.index.append(u3, p3, 0, bytes=True)
        self.index.append(u1, p4, 1, bytes=True)
        self.index.append(u2, p5, 2, bytes=True)
        self.index.append(u3, p6, 3, bytes=True)
        self.index.append(u3, p7, 6, bytes=True)
        self.index.append(u2, p8, 5, bytes=True)
        self.index.append(u2, p9, 8, bytes=True)

        user_last_post = blist.sortedlist([9, 7, 4])

        result = list()

        while user_last_post:
            b = self.index.get_block(user_last_post.pop())
            result.append(b.id)
            b.prev_p and user_last_post.add(b.prev_p)

        self.assertListEqual([9, 8, 7, 6, 5, 4, 3, 2, 1], result)


    def test_perfomance_sorted_blist(self):
        users = self.create_index(1000000, 100000)

        friends = blist.sortedlist()
        for i in xrange(500):
            friends.add(users.pop(random.choice(users.keys())))

        result = list()

        i = 0
        skip, limit = 1000, 10
        start_time = time.time()
        while friends and i < (skip + limit):
            b = self.index.get_block(friends.pop())
            if i > skip:
                result.append(b.id)
            b.prev_p and friends.add(b.prev_p)
            i += 1
        print '%.6f' % (time.time() - start_time)

        print result



