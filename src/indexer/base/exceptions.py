
class NotConfigured(BaseException):
    message = "Object is not configured: %s"

    def __init__(self, sub_message):
        super(NotConfigured, self).__init__(self.message % sub_message)