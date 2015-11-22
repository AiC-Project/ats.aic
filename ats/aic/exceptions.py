
class AICException(Exception):
    pass


class BuildFailure(AICException):
    pass


class MissingDirectoryFailure(AICException):
    pass


class ExecutionFailure(AICException):
    pass


class ConfigurationError(AICException):
    pass
