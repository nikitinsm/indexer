import os


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
        self.mode = read_only and 'rb' or 'ab+'
        directory = os.path.dirname(path)

        try:
            os.makedirs(directory)
        except OSError:
            if os.path.exists(directory) and os.path.isdir(directory):
                try:
                    self.handler = open(self.path, self.mode)
                except IOError:
                    raise
            else:
                raise

    def get(self, size, address=None):
        if address >= 0:
            self.handler.seek(address)
        return self.handler.read(size)

    def set(self, data, address=None):
        if address >= 0:
            self.handler.seek(address)
        self.handler.write(data)
        return True

    def commit(self):
        self.handler.flush()
        os.fsync(self.handler.fileno())

    def close(self):
        self.commit()
        self.handler.close()

