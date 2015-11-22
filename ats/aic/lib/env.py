
import pollute
from six.moves import shlex_quote


def stringify_dict(d):
    """Return a dict with values converted to strings,
    including pathlib.Path objects.
    """
    ret = {}
    for k, v in d.iteritems():
        try:
            ret[k] = v.as_posix()
        except AttributeError:
            ret[k] = str(v)
    return ret


def print_env(export, unset=()):
    """Prints an environment file to be sourced from the shell.
    """
    export = stringify_dict(export)
    for key in sorted(export):
        print('export {}={}'.format(key, shlex_quote(export[key])))
    for key in sorted(unset):
        print('unset {}'.format(key))


def environment(added=None, absent=()):
    """Context manager that modifies the environments variables.
    Path objects as values are replaced with strings.
    """
    added = stringify_dict(added or {})
    return pollute.modified_environ(added, absent)
