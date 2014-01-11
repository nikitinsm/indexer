import os
import timeit
import unittest
from indexer.base.storage import FileStorage


class TestFileStorageBase(unittest.TestCase):

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

    def test_with(self):
        with FileStorage(self.path) as fs:
            fs.set('data', 0)
            fs.commit()
            data = fs.get(4, 0)
            self.assertEqual('data', data)
        self.assertEqual(True, fs.handler.closed)

    def test_truncate(self):
        with FileStorage(self.path) as fs:
            fs.set('data', 0)
            fs.commit()

            fs.truncate()
            fs.commit()
            self.assertEqual(0, os.fstat(fs.handler.fileno()).st_size)

    def test_yield(self):
        with FileStorage(self.path) as fs:
            data_list = ['data%02d' % i for i in xrange(10)]
            for i, data in enumerate(data_list):
                fs.set(data, i * len(data))

            fs.commit()

            result = []
            for i in fs.read_from_end(6):
                result.append(i)

            result.reverse()
            self.assertListEqual(data_list, result)

    def _test_performance_1(self):
        data = 'test'
        times = 10 ** 5
        with FileStorage(self.path) as fs:
            def test_wo_fsync():
                fs.set(data)

            result = timeit.timeit(test_wo_fsync, number=times)

            self.assertLess(result, .2)

            def test_w_fsync():
                fs.set(data)
                fs.commit()

            result = timeit.timeit(test_w_fsync, number=times)

            self.assertLess(result, .5)
