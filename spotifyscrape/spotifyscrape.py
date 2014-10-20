# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""bootstrap.bootstrap: provides entry point main()."""


__version__ = "0.2.0"


import sys
import logging
from argh import *
import argcomplete
from .spotifyexport import export

def main():
    parser = ArghParser()
    parser.add_commands([export])
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    completion.autocomplete(parser)
    parser.dispatch()
