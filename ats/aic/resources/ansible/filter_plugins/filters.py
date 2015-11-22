
import pipes


def to_sh_environment(a, *args, **kw):
    lines = [
        'export %s=%s' % (key, pipes.quote(str(value)))
        for key, value in sorted(a.items())
    ]
    return '%s\n' % '\n'.join(lines)


def to_supervisor_environment(a, *args, **kw):
    lines = [
        '    %s = "%s"' % (key, value)
        for key, value in sorted(a.items())
    ]
    return '\n%s' % ',\n'.join(lines)


class FilterModule(object):
    def filters(self):
        return {
            'to_sh_environment': to_sh_environment,
            'to_supervisor_environment': to_supervisor_environment
        }
