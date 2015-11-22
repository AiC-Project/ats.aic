
import socket
import errno
import time


def wait_net_service(host_fn, port, timeout=None, logger=None):
    """ Wait for network service to appear
        @param timeout: in seconds, if None or 0 wait forever
        @return: None or (host, port) tuple.
    """
    s = socket.socket()
    if timeout:
        # time module is needed to calc timeout shared between two exceptions
        end = time.time() + timeout

    while True:
        try:
            if timeout:
                next_timeout = end - time.time()
                if next_timeout < 0:
                    return False
                else:
                    s.settimeout(next_timeout)

            if callable(host_fn):
                host = host_fn()
            else:
                host = host_fn

            if host:
                s.connect((host, port))

        except socket.timeout as err:
            # this exception occurs only if timeout is set
            if timeout:
                return False

        except socket.error as err:
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if err.errno in [errno.EHOSTUNREACH, errno.ECONNREFUSED]:
                if logger:
                    logger.info('Waiting for port %s:%s...' %
                                (host or '???', port))
                time.sleep(5)
                continue
            if err.errno != errno.ETIMEDOUT:
                if logger:
                    logger.info('Timeout at port %s:%s' % (host, port))
                raise
        else:
            s.close()
            return (host, port)
