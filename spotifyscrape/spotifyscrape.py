# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""spotifyscrape.spotifyscrape: provides entry point main()."""

__version__ = "0.2.0"

import argparse
import logging
from argh import ArghParser
from .spotifyexport import exporttracks, exportplaylist, checktoken
from .allaccessimport import allaccessimport, allaccesslogin


# These arguments are used by this global dispatcher and each individual
# stand-alone commands.
COMMON_PARSER = argparse.ArgumentParser(add_help=False)
COMMON_PARSER.add_argument('--debug',
                           action='store_true',
                           default=False,
                           help="Enable debug logging.")

def main():
    """
    Main entrypoint for the application. Parses the command-line arguments the
    dispatches the correct methods.
    """
    parser = ArghParser(parents=[COMMON_PARSER])
    parser.add_commands( [ allaccessimport, allaccesslogin ], namespace="gmusic")
    parser.add_commands( [ exporttracks, checktoken, exportplaylist], namespace="spotify")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    parser.dispatch()
