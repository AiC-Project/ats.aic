import contextlib
import errno
import os

from ats.aic.exceptions import MissingDirectoryFailure


@contextlib.contextmanager
def pushd(path, if_missing=''):
    try:
        path = path.as_posix()
    except AttributeError:
        pass

    cwd = os.getcwd()

    try:
        os.chdir(path)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            message = 'Missing directory: %s' % path
            if if_missing:
                message += ' - ' + if_missing
            raise MissingDirectoryFailure(message)
        else:
            raise

    try:
        yield
    finally:
        os.chdir(cwd)
