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

APP_CONFIG_FILE = os.path.expanduser("~/.spotifyscrape")

@arg('--username', help='The username to use when logging into All Access account. ' +
                        'Typically your Google email address.')
@arg('--password', help='The password for the All Access account. If you use two factor ' +
                        'authentication generate an application password.')
@arg('--dry-run', help='Do not make any actual changes in All Access.')
@arg('--stdin', help='Read the input from STDIN. The PLAYLIST argument will become the playlist name.')
@arg('playlist', help='The CSV file that contains the tracks to add. The file name (without extension) ' +
                      'will become the playlist name. If --stdin flag is set, this is the playlist name.')
@named('import')
def allaccessimport(playlist, username=None, password=None, dry_run=False, stdin=False):
    """
    Exports a Spotify playlist to stdout or csv.
    """

    # Try to get user name from config
    if not username or not password:
        username, password = read_config()

    if not username or not password:
        raise CommandError("Username and password must be provided as either command-line argument or in the application configuration file.")
    logging.debug("Username={}".format(username))

    if not stdin and not os.path.exists(playlist):
        raise CommandError("The playlist file does not exist.")

    playlist_name = playlist
    if not stdin:
        playlist_name = os.path.basename(playlist_name)
        playlist_name = os.path.splitext(playlist_name)[0]
    logging.debug("Playlist name will be: {}".format(playlist_name))

    api = Mobileclient(False, False)
    logged_in = api.login(username, password)
    if not logged_in:
        raise CommandError('Error. Unable to login to Google Music All Access.')

    playlist_ref, currenttracks = get_playlist(api, playlist_name)

    if not playlist_ref and not dry_run:
        sys.stderr.write('Playlist not found. Creating new.\n')
        playlist_ref = api.create_playlist(playlist_name)

    yield 'Going to update playlist {0} ({1})\n'.format(playlist_name, playlist_ref)

    failed_tracks = list()
    songs_added = 0
    total = 0

    if stdin:
        stream = sys.stdin
    else:
        stream = open(playlist, "rb")

    for kw in stream:
        kw = re.sub('\r\n', '', kw)

        x = list(csv.reader([kw], quoting=csv.QUOTE_ALL))[0]

        if x[0] == 'Track' and x[1] == 'Artist':
            yield 'Skipping header.'
            continue

        search_term = "{0} {1}".format(x[0], x[1])


        total = total + 1

        newtrackid, error_reason = search_track(api, search_term, currenttracks)

        if newtrackid:
            if not dry_run:
                api.add_songs_to_playlist(playlist_ref, newtrackid)
            songs_added = songs_added + 1
        else:
            failed_tracks.append(x)

        sys.stderr.write("Searching {}...{}".format(search_term, error_reason))


    yield "{0} songs added out of {1}. {2} Failed.".format(songs_added, total, total-songs_added)

    yield "Failed tracks:"
    for line in failed_tracks:
        print "  ", line

def search_track(api, search_term, currenttracks):
    try:
        results = api.search_all_access(search_term)
    except Exception as error:
        logging.exception(e)
        return None, "Search Failed"

    if len(results['song_hits']) > 0:
        if results['song_hits'][0]['score'] > 50:
            newtrackid = results['song_hits'][0]['track']['nid']

            if newtrackid in currenttracks:
                return None, "Dupe"
            else:
                return newtrackid, "OK"
        else:
            sys.stderr.write("Got track {0} with low score {1}.\n".format(results['song_hits'][0]['track']['title'], results['song_hits'][0]['score']))
            return None, "No Results in Threshold"
    else:
        sys.stderr.write("Nothing good found.\n")
        return None, "No Results"


def get_playlist(api, playlistname):
    playlist = [x for x in api.get_all_user_playlist_contents() if x['name'] == playlistname]
    currenttracks = list()

    if len(playlist) == 1:
        tracks = playlist[0]['tracks']
        currenttracks = [x['track']['storeId'] for x in tracks]

        playlist = playlist[0]['id']
        sys.stderr.write('Playlist named {} exists. It will be updated.\n'.format(playlistname))
    else:
        playlist = None

    return playlist, currenttracks

def read_config():
    username = None
    password = None
    if os.path.exists(APP_CONFIG_FILE):
        with open(APP_CONFIG_FILE, 'r') as config_f:
            json_data = config_f.read()
            try:
                data = json.loads(json_data)
            except ValueError as error:
                raise CommandError("The configuration file at ~/.spotifyscrape could not be read. It maybe empty or invalid")

            username = data['username']
            password = data['password']
    else:
        logging.debug("Config file '{}' not found".format(APP_CONFIG_FILE))

    return username, password
