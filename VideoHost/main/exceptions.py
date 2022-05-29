class AwsFileNotFoundError(BaseException):

    def __init__(self, status_code, message=None):
        self.message = message
        self.status_code = status_code

    def __call__(self):
        raise self



class XMPPUserCreationFailed(BaseException):
    pass



class XMPPUserDeleteFailed(BaseException):
    pass



class XMPPGroupCreationFailed(BaseException):
    pass



class XMPPGroupDeleteFailed(BaseException):
    pass

