class DropboxBucketDoesNotExist(BaseException):
    pass

class DropboxFileNotFound(BaseException):
    pass

class DropboxFileUploadFailed(BaseException):
    pass

class DropboxFileRemoveFailed(BaseException):
    pass