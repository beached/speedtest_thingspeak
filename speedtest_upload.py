# !/usr/bin/python
__requires__ = 'speedtest-cli==0.3.4'
import os
import signal
import socket
import speedtest_cli
import sys
import threading

# Some global variables we use
user_agent = None
source = None
shutdown_event = None
scheme = 'http'
# Used for bound_interface
socket_socket = socket.socket

try:
    import xml.etree.cElementTree as ET
except ImportError:
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        from xml.dom import minidom as DOM

        ET = None

# Begin import game to handle Python 2 and Python 3
try:
    from urllib2 import urlopen, Request, HTTPError, URLError
except ImportError:
    from urllib.request import urlopen, Request, HTTPError, URLError

try:
    from httplib import HTTPConnection, HTTPSConnection
except ImportError:
    e_http_py2 = sys.exc_info()
    try:
        from http.client import HTTPConnection, HTTPSConnection
    except ImportError:
        e_http_py3 = sys.exc_info()
        raise SystemExit('Your python installation is missing required HTTP '
                         'client classes:\n\n'
                         'Python 2: %s\n'
                         'Python 3: %s' % (e_http_py2[1], e_http_py3[1]))

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from urlparse import parse_qs
except ImportError:
    try:
        from urllib.parse import parse_qs
    except ImportError:
        from cgi import parse_qs

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

try:
    import builtins
except ImportError:
    def print_(*args, **kwargs):
        """The new-style print function taken from
        https://pypi.python.org/pypi/six/

        """
        fp = kwargs.pop("file", sys.stdout)
        if fp is None:
            return

        def write(data):
            if not isinstance(data, basestring):
                data = str(data)
            fp.write(data)

        want_unicode = False
        sep = kwargs.pop("sep", None)
        if sep is not None:
            if isinstance(sep, unicode):
                want_unicode = True
            elif not isinstance(sep, str):
                raise TypeError("sep must be None or a string")
        end = kwargs.pop("end", None)
        if end is not None:
            if isinstance(end, unicode):
                want_unicode = True
            elif not isinstance(end, str):
                raise TypeError("end must be None or a string")
        if kwargs:
            raise TypeError("invalid keyword arguments to print()")
        if not want_unicode:
            for arg in args:
                if isinstance(arg, unicode):
                    want_unicode = True
                    break
        if want_unicode:
            newline = unicode("\n")
            space = unicode(" ")
        else:
            newline = "\n"
            space = " "
        if sep is None:
            sep = space
        if end is None:
            end = newline
        for i, arg in enumerate(args):
            if i:
                write(sep)
            write(arg)
        write(end)
else:
    print_ = getattr(builtins, 'print')
    del builtins


def ctrl_c(signum, frame):
    """Catch Ctrl-C key sequence and set a shutdown_event for our threaded
    operations
    """

    global shutdown_event
    shutdown_event.set()
    raise SystemExit('\nCancelling...')


def do_test(timeout=10, use_secure=False):
    global shutdown_event, source, scheme
    shutdown_event = threading.Event()

    signal.signal(signal.SIGINT, ctrl_c)

    socket.setdefaulttimeout(timeout)

    # Pre-cache the user agent string
    speedtest_cli.build_user_agent()

    if use_secure:
        speedtest_cli.scheme = 'https'

    try:
        config = speedtest_cli.getConfig()
    except speedtest_cli.URLError:
        print_('Cannot retrieve speedtest configuration')
        sys.exit(1)

    servers = speedtest_cli.closestServers(config['client'])

    try:
        best = speedtest_cli.getBestServer(servers)
    except IndexError:
        print_('Invalid server ID')
        sys.exit(1)
    result_ping = best['latency']

    sizes = [350, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
    urls = []
    for size in sizes:
        for i in range(0, 4):
            urls.append('%s/random%sx%s.jpg' %
                        (os.path.dirname(best['url']), size, size))
    dlspeed = speedtest_cli.downloadSpeed(urls, True)

    result_dl_speed = dlspeed / 125000

    sizesizes = [int(.25 * 1000 * 1000), int(.5 * 1000 * 1000)]
    sizes = []
    for size in sizesizes:
        for i in range(0, 25):
            sizes.append(size)
    ulspeed = speedtest_cli.uploadSpeed(best['url'], sizes, True)

    result_ul_speed = ulspeed / 125000
    return (result_ping, result_dl_speed, result_ul_speed)


def main():
    try:
        result = do_test(use_secure=True)
        print "results: %s" % (result,)
    except KeyboardInterrupt:
        print_('\nCancelling...')


if __name__ == '__main__':
    main()

#
