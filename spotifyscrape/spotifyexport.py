#!/usr/bin/env python

# NOTE: Idea for this script came from:
# spotify-export (https://github.com/jlund/spotify-export)

import HTMLParser
import csv as csvlib
import json, codecs
import mechanize
import os
import re
import sys
import urllib2
import logging

from argh import *
from collections import namedtuple


@arg('--csv', action='store_true', default=False, help="Save the results to a CSV file. This option is redundant if you specify the CSVFILE argument. When this option is set the CSV file will have the same name as the input file.")
@arg('tracklist', help="A text file containing the Spotify URIs to track, one per line. See http://bit.ly/1pt3yVT for details.")
@arg('csvfile', default=None, nargs='?', help="The name of the CSV file to save the results. You can use the --csv option to save the results to TRACKLIST.csv. If both this argument and --csv are omitted the results will be printed to the standard output.")
def export(tracklist, csvfile, csv=False):
    """
    Exports a Spotify playlist
    """

    html_parser = HTMLParser.HTMLParser()

    if csv and not csvfile:
        base = os.path.basename(tracklist)
        base = os.path.splitext(base)[0]
        csvfile = '{}.csv'.format(base)

    txt_element = lambda obj: obj.text if obj is not None else ''

    total = 0
    success = 0

    if csvfile:
        wr = csvlib.writer(open(csvfile, mode='wb'), quoting=csvlib.QUOTE_ALL)
        sys.stderr.write('Also writing to CSV file: {}\n'.format(csvfile))
    else:
        wr = csvlib.writer(sys.stdout, quoting=csvlib.QUOTE_ALL)

    wr.writerow(["Track", "Artist", "Album"])

    with open(tracklist, 'r') as fp:
        print_header = True

        for line in fp.readlines():
            total = total + 1
            line = re.sub('\r\n', '', line)
            line = line.strip()

            if not line or len(line) <= 0:
                continue

            # See https://developer.spotify.com/technologies/web-api/lookup/
            line = 'http://ws.spotify.com/lookup/1/.json?uri={0}'.format(line)

            logging.debug('Fetching %s\n' % (line))

            try:
                data = mechanize.urlopen(line).read()
            except urllib2.HTTPError as e:
                logging.debug(str(e) + "\n")
                continue

            x = json.loads(data)

            if not x['track']:
                continue

            track = x['track']['name'].encode('utf8')
            album = x['track']['album']['name'].encode('utf8')
            artist = x['track']['artists'][0]['name'].encode('utf8')

            success = success + 1

            wr.writerow([track, artist, album])

            if csvfile:
                # Informative output
                print ','.join([track, artist, album])
            else:
                # Make sure user can see what we're piping out
                sys.stdout.flush()

    sys.stderr.write("{0} tracks processed. {1} found. {2} failed.\n".format(total, success, total - success))

