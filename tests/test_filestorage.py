import os
import timeit
import unittest
from indexer.base.storage import FileStorage


class TestBase(unittest.TestCase):

    path = '/tmp/indexer/test.ix'

    def setUp(self):
        try:
            os.unlink(self.path)
        except OSError:
            pass

    def test_open_rw(self):

        f = FileStorage(self.path)
        f.close()

        self.assertEqual(True, os.path.exists(f.path))

    def test_read_write(self):
        data = 'test'

        f = FileStorage(self.path)
        f.set(data)
        f.commit()

        result = f.get(len(data), 0)

        self.assertEquals(data, result)

        f.close()

    def test_performance_1(self):
        data = 'test'
        times = 10 ** 5
        f = FileStorage(self.path)
        def test_wo_fsync():
            f.set(data)

        result = timeit.timeit(test_wo_fsync, number=times)

        self.assertLess(result, .2)

        def test_w_fsync():
            f.set(data)
            f.commit()

        result = timeit.timeit(test_w_fsync, number=times)

        self.assertLess(result, .4)

        f.close()