"""
Usage:
    autocomment trustie [--log-file=<f> --log-level=<l>]
                        [--conf-file=<cf>]
                        [--stop-if-praised --force-comment]
                        [--start-page=<p>]

Auto-comment is a tool to post comment to a site automatically. Right now only
trustie.net is implemented.

Logging options:
    --log-file=<f>      Path of log file [default: ~/.autocomment.log]
    --log-level=<l>     Logging level. The file logging level, not console
                        logging level. [default: INFO]

Options for trustie are:
    --conf-file=<cf>    The configuration file. [default: ~/.autocomment.conf]
    --stop-if-praised   Stop scraping if confront a praise news.
    --force-comment     Force add comment even if it is praised.
    --start-page=<p>    Start page number. [default: 1]

The working flow of auto comment for trustie is:
    (0) Find news links and for each do the following:
        (1) Find praise element. If not found, skip this news.
        (2) If not praised, do praise, go to (3); if praised
            (2-1) If `--stop-if-praised` is set, stop the whole loop
            (2-2) Else if `--force-comment` is set, go to (3)
            (2-3) Else skip this news
        (3) Find comment element and do comment.
"""
import logging
import sys
from os.path import expanduser
from logging.handlers import RotatingFileHandler

from docopt import docopt
from schema import Schema, SchemaError, Use
import yaml

from . import VERSION
from .trustie import auto

logger = logging.getLogger()


def configure_logging(stream=None,
                      stream_level='DEBUG',
                      filename=None,
                      file_level='INFO'):
    """Configure the root logger by adding streaming handler and file handler.
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    # clear root
    root = logging.getLogger()
    root.setLevel('DEBUG')
    for h in root.handlers:
        root.removeHandler(h)
    if stream is not None:
        sh = logging.StreamHandler(stream=stream)
        sh.setLevel(stream_level)
        sh.setFormatter(formatter)
        root.addHandler(sh)
    if filename is not None:
        fh = RotatingFileHandler(
            filename, maxBytes=10 * 1024 * 1024, backupCount=3)
        fh.setLevel(file_level)
        sh.setFormatter(formatter)
        root.addHandler(fh)


def main(argv=None):
    """The main entry point of command line interface."""
    args_schema = Schema({'--start-page': Use(int), object: object})
    args = docopt(__doc__, version=VERSION, argv=argv or sys.argv[1:])
    try:
        args = args_schema.validate(args)
    except SchemaError as e:
        raise SystemExit(e)
    # set logging level
    args['--conf-file'] = expanduser(args['--conf-file'])
    args['--log-file'] = expanduser(args['--log-file'])
    configure_logging(
        stream=sys.stdout,
        filename=args['--log-file'],
        file_level=args['--log-level'])
    with open(args['--conf-file']) as f:
        conf = yaml.load(f)

    if args['trustie'] is True:
        auto(
            conf,
            stop_if_praised=args['--stop-if-praised'],
            force_comment=args['--force-comment'],
            start_page=args['--start-page'])
    else:
        raise SystemExit('Invalid subcommand, try `autocomment -h`')
