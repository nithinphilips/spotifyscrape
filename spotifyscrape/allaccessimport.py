#!/usr/bin/python
import re, sys
import csv
import os.path
import json
import logging

from .config import read_config
from argh import *
from gmusicapi import Mobileclient

APP_CONFIG_FILE = os.path.expanduser("~/.spotifyscrape")

@arg('--username', help='The username to use when logging into All Access account. ' +
                        'Typically your Google email address.', default=read_config().get("All Access", "username"))
@arg('--password', help='The password for the All Access account. If you use two factor ' +
                        'authentication generate an application password.', default=read_config().get("All Access", "password"))
@arg('--dry-run', help='Do not make any actual changes in All Access.')
@arg('--playlist', help='The CSV file that contains the tracks to add. The file name (without extension) ' +
                      'will become the playlist name. If --stdin flag is set, this is the playlist name.')
@named('import')
def allaccessimport(playlist=None, username=None, password=None, dry_run=False, stdin=False):
    """
    Exports a Spotify playlist to stdout or csv.
    """

    if not username or not password:
        raise CommandError("Username and password must be provided as either command-line argument or in the application configuration file.")

    playlist_name = playlist
    if playlist:
        playlist_name = os.path.basename(playlist_name)
        playlist_name = os.path.splitext(playlist_name)[0]
    logging.debug("Playlist name will be: {}".format(playlist_name))

    api = Mobileclient(False, False)
    logged_in = api.login(username, password)
    if not logged_in:
        raise CommandError('Error. Unable to login to Google Music All Access.')

    playlist_ref = None
    currenttracks = None

    failed_tracks = list()
    songs_added = 0
    total = 0

    stream = open(playlist, "rb") if playlist else sys.stdin

    for kw in stream:
        kw = kw.strip()

        if kw.startswith("#"):
            data = kw[1:]
            parts = [x.strip() for x in data.split(":")]
            if(len(parts) == 2):
                if(parts[0] == "Playlist"):
                    playlist_name = parts[1]
            continue

        if not playlist_ref:
            if not playlist_name:
                raise CommandError("A playlist name was not given and it was not found in the file either. Can't continue.")
            else:
                playlist_ref, currenttracks = get_playlist(api, playlist_name)
                if not playlist_ref and not dry_run:
                    sys.stderr.write('Playlist not found. Creating new.\n')
                    playlist_ref = api.create_playlist(playlist_name)
                yield 'Going to update playlist {0} ({1})\n'.format(playlist_name, playlist_ref)

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
        sys.stderr.write("Searching {}...{}\n".format(search_term, error_reason))


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
            return None, "No Results within Threshold"
    else:
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
