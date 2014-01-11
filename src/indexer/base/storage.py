import os
import uuid


class BaseStorage(object):

    def get(self, size, address):
        raise NotImplementedError()

    def set(self, data, address):
        raise NotImplementedError()


class FileStorage(BaseStorage):

    path = None
    mode = None
    handler = None

    def __init__(self, path, read_only=False):
        self.path = path
        self.mode = read_only and 'rb' or 'rb+'
        directory = os.path.dirname(path)

        try:
            os.makedirs(directory)
        except OSError:
            if os.path.exists(directory) and os.path.isdir(directory):
                #create DB if not exists
                if not os.path.exists(self.path):
                    open(self.path, 'a').close()
                #open storage file
                try:
                    self.handler = open(self.path, self.mode)
                except IOError:
                    raise
            else:
                raise

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def get(self, size, address=None):
        if address >= 0:
            self.handler.seek(address, os.SEEK_SET)
        return self.handler.read(size)

    def set(self, data, address=None):
        if address >= 0:
            self.handler.seek(address, os.SEEK_SET)
        self.handler.write(data)
        return True

    def commit(self):
        self.handler.flush()
        os.fsync(self.handler.fileno())

    def close(self):
        self.commit()
        self.handler.close()

    def truncate(self):
        self.handler.truncate(0)

    def delete(self):
        os.unlink(self.path)

    def read_from_end(self, size=None, limit=None):
        assert size > 0

        offset = size

        while True:
            try:
                self.handler.seek(-offset, os.SEEK_END)
            except IOError:
                break
            result = self.handler.read(size)
            yield result
            offset += size
            #limit -= 1

    def find_from_end(self, block_size, col_offset=0, match_size=1, match=None, limit=10):
        skanned = 1
        for block in self.read_from_end(block_size):
            if limit <= 0:
                break
            to_match = block[col_offset:col_offset+match_size]
            #print uuid.UUID(bytes=to_match)
            if to_match in match:
                yield skanned, block
                limit -= 1
            skanned += 1





