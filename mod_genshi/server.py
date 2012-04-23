"""mod_genshi development server.
"""
from wsgiref.simple_server import make_server
from functools import partial
import optparse
import os
import socket
import sys
import time
import webbrowser

from mod_genshi.app import handler

__all__ = []


def parse_command_line(cmdline=None):
    "Parse command line"
    usage = "Usage: python -m mod_genshi.server [options]"
    cmdline = cmdline if cmdline is not None else sys.argv[1:]
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--port", type="int", default=8000,
        help="Port that server will listen on")
    parser.add_option("-b", "--window", action="store_true", default=False,
        help="Open a current web browser window for the server")
    parser.add_option("-w", "--newwindow", action="store_true", default=False,
        help="Open a new web browser window for the server")
    parser.add_option("-t", "--newtab", action="store_true", default=False,
        help="Open a new web browser tab for the server")
    parser.add_option("-r", "--autoraise", action="store_true", default=False,
        help="Auto raise the web browser")
    opts, args = parser.parse_args(cmdline)
    return opts


def open_browser_cmd(opts):
    "Create command to open web browser"
    url = "http://{0}:{1}".format(socket.gethostname(), opts.port)
    if opts.window:
        return partial(webbrowser.open, url, new=0, autoraise=opts.autoraise)
    elif opts.newwindow:
        return partial(webbrowser.open, url, new=1, autoraise=opts.autoraise)
    elif opts.newtab:
        return partial(webbrowser.open, url, new=2, autoraise=opts.autoraise)
    return None


if __name__ == '__main__':
    opts = parse_command_line()
    command = open_browser_cmd(opts)
    if command is not None and os.fork() == 0:
        time.sleep(0.5)
        command()
        sys.exit(0)
    try:
        sys.stdout.write("Serving on port {0} ...\n".format(opts.port))
        httpd = make_server('', opts.port, handler)
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
