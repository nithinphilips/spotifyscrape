# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""bootstrap.bootstrap: provides entry point main()."""


__version__ = "0.2.0"


import sys
from argh import *
import argcomplete
from .spotifyexport import export
from .allaccessimport import allaccessimport

def main():
    parser = ArghParser()
    parser.add_commands([export, allaccessimport])
    completion.autocomplete(parser)
    parser.dispatch()
