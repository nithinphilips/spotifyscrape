import ConfigParser, os, logging

APP_CONFIG_FILE = os.path.expanduser("~/.spotifyscrape")

config = None

def read_config():
    global config
    if not config:
        if os.path.exists(APP_CONFIG_FILE):
            config = ConfigParser.SafeConfigParser()
            config.readfp(open(os.path.join(os.path.dirname(__file__), 'defaults.conf')))
            config.read(['/etc/spotifyscrape.conf', APP_CONFIG_FILE])
        else:
            logging.debug("Config file '{}' not found".format(APP_CONFIG_FILE))

    return config
