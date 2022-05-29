class AwsFileNotFoundError(BaseException):

    def __init__(self, status_code, message=None):
        self.message = message
        self.status_code = status_code

    def __call__(self):
        raise self

class AwsInvalidFilelinkError(BaseException):
    pass

class AwsDeleleFailed(BaseException):
    pass