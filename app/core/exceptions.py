class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidFileTypeException(AppException):
    pass


class MissingDrugColumnException(AppException):
    pass


class FileTooLargeException(AppException):
    pass


class RxNavServiceException(AppException):
    pass
