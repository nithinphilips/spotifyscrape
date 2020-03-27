# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""Methods to read the app configuration"""

import configparser, os

APP_CONFIG_FILE = os.path.expanduser("~/.spotifyscrape")

CONFIG = None

def read_config():
    """
    Read the configuration file and load the configuration
    or return an already loaded configuration object.
    """
    global CONFIG
    if not CONFIG:
        CONFIG = configparser.ConfigParser()
        CONFIG.readfp(
            open(os.path.join(
                os.path.dirname(__file__),
                'defaults.conf'
            ))
        )
        CONFIG.read(['/etc/spotifyscrape.conf', APP_CONFIG_FILE])

    return CONFIG

