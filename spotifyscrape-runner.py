#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK


"""Convenience wrapper for running bootstrap directly from source tree."""


from spotifyscrape.spotifyscrape import main
import logging

debug = False

if __name__ == '__main__':
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    main()
