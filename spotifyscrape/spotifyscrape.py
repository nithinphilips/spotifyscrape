# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""bootstrap.bootstrap: provides entry point main()."""


__version__ = "0.2.0"


import sys
from argh import *
import argparse
import logging
from .spotifyexport import exporttracks, exportplaylist, checktoken
from .allaccessimport import allaccessimport


# These arguments are used by this global dispatcher and each individual stand-alone commands.
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument('--debug',
                           action='store_true',
                           default=False,
                           help="Enable debug logging.")

def main():
    parser = ArghParser(parents=[common_parser])
    parser.add_commands([exporttracks, checktoken, allaccessimport, exportplaylist])

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

    parser.dispatch()
