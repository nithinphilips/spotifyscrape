#!/usr/bin/python
import re, sys
import argparse
import csv
import fileinput
import os.path
import codecs
import json
import logging

from argh import *
from gmusicapi import Mobileclient
from pprint import pprint

debug = True


@arg('--username', default='')
@arg('--password', default='')
@arg('--dry-run', default=False, action='store_true')
@arg('playlistfile')
@named('import')
def allaccessimport(playlistfile, username=None, password=None, dry_run=False):
    """
    Exports a Spotify playlist to stdout or csv.
    """

    # Try to get user name from config
    config_file = os.path.expanduser("~/.spotifyscrape")
    if username and password:
        logging.debug("Not lookin for config file since both usr name and password are given as commandline options")
    else:
        if os.path.exists(config_file):
            with open(config_file, 'r') as config_f:
                json_data = config_f.read()
                try:
                    data = json.loads(json_data)
                except ValueError as error:
                    raise CommandError("The configuration file at ~/.spotifyscrape could not be read and you did not specfiy the username and password in the arguments.")
                username = data['username']
                password = data['password']
        else:
            logging.debug("Config file not found")

    if not os.path.exists(playlistfile):
        raise CommandError('The given playlist file "{}" does not exist'.format(playlistfile))

    playlistname = playlistfile
    playlistname = os.path.basename(playlistname)
    playlistname = os.path.splitext(playlistname)[0]

    logging.debug("Playlist name will be: {}".format(playlistname))

    api = Mobileclient(False, False)
    logged_in = api.login(username, password)

    if not logged_in:
        raise CommandError('Error. Unable to login to Google Music.')


    # 1. See if the playlist already exists.
    playlist = [x for x in api.get_all_user_playlist_contents() if x['name'] == playlistname]
    currenttracks = list()

    if len(playlist) == 1:
        tracks = playlist[0]['tracks']
        currenttracks = [x['track']['storeId'] for x in tracks]

        playlist = playlist[0]['id']
        yield 'Playlist found. It will be updated.'
    else:
        yield 'Playlist not found. Creating new.'
        playlist = api.create_playlist(playlistname)


    yield 'Will update playlist {0} ({1})\n'.format(playlistname, playlist)

    failed_tracks = list()
    songs_added = 0
    total = 0

    if os.path.isfile(playlistfile):
        stream = open(playlistfile, "rb")
        yield 'A file matching the playlist name was found. It will used instead of STDIN'
    else:
        stream = sys.stdin

    for kw in stream:
        kw = re.sub('\r\n', '', kw)

        x = list(csv.reader([kw], quoting=csv.QUOTE_ALL))[0]

        if x[0] == 'Track' and x[1] == 'Artist':
            yield 'Skipping header.'
            continue

        search_term = "{0} {1}".format(x[0], x[1])

        sys.stderr.write("Searching {0}...".format(search_term))

        total = total + 1
        try:
            results = api.search_all_access(search_term)
        except:
            sys.stderr.write("No results\n")
            failed_tracks.append(x)
            continue

        if len(results['song_hits']) > 0:
            if results['song_hits'][0]['score'] > 50:
                newtrackid = results['song_hits'][0]['track']['nid']

                if newtrackid in currenttracks:
                    sys.stderr.write("Dupe. Skip.\n")
                else:
                    if not dry_run:
                        api.add_songs_to_playlist(playlist, newtrackid)
                    else:
                        sys.stderr.write("NOOP")
                    #sys.stderr.write(newtrackid)
                    sys.stderr.write("OK.\n")
                    songs_added = songs_added + 1
            else:
                sys.stderr.write("Got track {0} with low score {1}.\n".format(results['song_hits'][0]['track']['title'], results['song_hits'][0]['score']))
        else:
            sys.stderr.write("Nothing good found.\n")
            failed_tracks.append(x)

    yield "{0} songs added out of {1}. {2} Failed.".format(songs_added, total, total-songs_added)

    yield "Failed tracks:"
    for line in failed_tracks:
        yield "  " + line
