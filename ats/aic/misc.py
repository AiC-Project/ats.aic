
import errno
import logging
from pathlib import Path
import shutil
import subprocess

from six.moves import shlex_quote

from cliff.command import Command
from cliff.lister import Lister

from ats.aic.exceptions import ExecutionFailure


def stringify_cmdline_parts(args):
    ret = []

    # convert Path and integer objects to strings
    for part in args:
        try:
            if isinstance(part, int):
                part = str(part)
            else:
                part = part.as_posix()
        except AttributeError:
            pass
        finally:
            ret.append(part)

    return ret


def escaped_cmdline(parts):
    return ' '.join(shlex_quote(s) for s in parts)


def log_cmdline(cmdline, logger, log_level='DEBUG'):
    if not isinstance(log_level, int):
        log_level = logging.getLevelName(log_level)
    logger.log(log_level, 'Running: %s', cmdline)


def wrap_call(*args, **kw):
    """Wraps Popen.communicate() while also logging the command line.

    Converts Path and numeric arguments to strings.
    Accepts a 'log_level' argument which defaults to DEBUG.
    """

    kw = kw.copy()
    capture_out = kw.pop('capture_out', False)
    capture_err = kw.pop('capture_err', False)
    logger = kw['logger']

    args = stringify_cmdline_parts(args)
    cmdline = escaped_cmdline(args)
    log_cmdline(cmdline, logger, kw.pop('log_level', 'DEBUG'))

    try:
        proc = subprocess.Popen(args,
                                stdout=[
                                    None, subprocess.PIPE
                                ][capture_out],
                                stderr=[
                                    None, subprocess.PIPE
                                ][capture_err])
        result = proc.communicate()
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise ExecutionFailure('Command not found: %s' % cmdline)
        else:
            raise

    if proc.returncode:
        raise ExecutionFailure('Command failed (status %s): %s' %
                               (proc.returncode, cmdline))

    ret = {}
    if capture_out:
        ret['output'] = result[0]
    if capture_err:
        ret['error'] = result[1]
    return ret


class AICMixin:
    @property
    def log(self):
        return self.app.LOG

    @property
    def conf(self):
        return self.app.conf

    @property
    def local_etc(self):
        return Path(self.app.workpath, 'etc')

    @property
    def secrets_dir(self):
        return Path(self.app.workpath, 'secrets', self.conf.cluster)

    @property
    def local_src(self):
        ret = Path(self.app.workpath, 'src')
        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def local_images(self):
        ret = Path(self.app.workpath, 'images')
        if not ret.exists():
            ret.mkdir(parents=True)
        return ret

    @property
    def private_ssh_key(self):
        return Path(self.local_etc, self.conf.ssh_key_file)

    def call(self, *args, **kw):
        if not isinstance(args[0], basestring):
            raise ValueError('not a string: %s' % args[0])

        kw = kw.copy()
        if 'logger' not in kw:
            kw['logger'] = self.log
        return wrap_call(*args, **kw)

    def copy_file(self, path1, path2, log_level='DEBUG'):
        if not isinstance(log_level, int):
            log_level = logging.getLevelName(log_level)
        self.log.log(log_level, 'Copying: %s -> %s', path1, path2)
        shutil.copy(path1.as_posix(), path2.as_posix())


class AICCommand(Command, AICMixin):
    pass


class AICLister(Lister, AICMixin):
    pass


def fetch_stackoutput(stack_name, parameter, logger):
    """
    Return an output parameter of the stack if present, None otherwise.
    """
    try:
        output = wrap_call(
            'openstack', 'stack', 'output', 'show',
            stack_name, parameter, '-f', 'value', '-c', 'output_value',
            capture_err=True,
            capture_out=True,
            logger=logger
        )['output']
    except ExecutionFailure:
        return
    return output.strip()
