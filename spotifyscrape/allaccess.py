# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""Module to work with Google Play All Access playlists"""

import csv
import os.path
import logging
import sys
import re
from urllib.parse import unquote

from .config import read_config
from argh import arg, named, CommandError
from gmusicapi import Mobileclient

APP_CONFIG_FILE = os.path.expanduser("~/.spotifyscrape")


@arg(
    '--client-id', help='A unique ID for this client',
    default=read_config().get("All Access", "client-id")
)
@arg("--shared",
     help="If set, the playlist name is treated as a shared playlist. "
          "If you use the Share URL, this is automatically set.")
@named('export')
def allaccessexport(playlist_name, client_id=None, shared=False):
    if not client_id:
        raise CommandError(
            "client-id must be provided as either command-line " +
            "argument or in the application configuration file."
        )

    api = Mobileclient(debug_logging=False, validate=False)
    logged_in = api.oauth_login(client_id)
    if not logged_in:
        raise CommandError('Error. Unable to login to Google Music All Access.')

    if playlist_name.startswith("http"):
        shared = True

    if playlist_name == "Thumbs Up":
        topsongs = api.get_top_songs()
        tp2 = list()
        for song in topsongs:
            tp2.append({'track': song})

        playlist = {
            'name': "Thumbs Up",
            'shareToken': '',
            'tracks': tp2
        }
    elif shared:
        pattern = r"https?://play.google.com/music/playlist/(.+)"
        match = re.match(pattern, playlist_name)
        if match:
            share_id = match.group(1)
            playlist_name = unquote(share_id)
        else:
            playlist_name = unquote(playlist_name)

        songs = api.get_shared_playlist_contents(playlist_name)

        playlist = {
            'name': "Shared",
            'shareToken': playlist_name,
            'tracks': songs
        }
    else:
        playlist = [x for x in api.get_all_user_playlist_contents() if x['name'] == playlist_name]
        if len(playlist) == 1:
            playlist = playlist[0]
        else:
            return "Playlist not found"

    tracks = playlist['tracks']
    playlist = playlist

    yield f"# Playlist: {playlist['name']}"
    yield f"# Description: from https://play.google.com/music/playlist/{playlist['shareToken']}"
    yield 'Track,Artist,Album'
    for track in tracks:
        if 'track' in track:
            track = track['track']
            yield f"{track['title']},{track['artist']},{track['album']}"
        else:
            sys.stderr.write(f"Unable to get track details: {track}\n")


@arg(
    '--client-id', help='A unique ID for this client',
    default=read_config().get("All Access", "client-id")
)
@arg(
    '--dry-run', help='Do not make any actual changes in All Access.'
)
@arg(
    '--playlist', help='The CSV file that contains the tracks to add. ' +
                       'The file name (without extension) will become the playlist name.'
)
@named('import')
def allaccessimport(playlist=None, client_id=None, dry_run=False):
    """
    Exports a Spotify playlist to stdout or csv.
    """

    if not client_id:
        raise CommandError(
            "client-id must be provided as either command-line " +
            "argument or in the application configuration file."
        )

    playlist_name = playlist
    playlist_description = ""
    if playlist:
        playlist_name = os.path.basename(playlist_name)
        playlist_name = os.path.splitext(playlist_name)[0]
    logging.debug(f"Playlist name will be: {playlist_name}")

    api = Mobileclient(debug_logging=False, validate=False)
    logged_in = api.oauth_login(client_id)
    if not logged_in:
        raise CommandError('Error. Unable to login to Google Music All Access.')

    playlist_ref = None
    currenttracks = None

    failed_tracks = list()
    songs_added = 0
    total = 0

    stream = open(playlist, "rb") if playlist else sys.stdin

    for input_line in stream:
        input_line = input_line.strip()

        # Lazily search the beginning of the file for a Playlist name
        if input_line.startswith("#"):
            data = input_line[1:]
            parts = [x.strip() for x in data.split(":", 1)]

            if len(parts) == 2:
                if parts[0] == "Playlist":
                    playlist_name = parts[1]
                elif parts[0] == "Description":
                    playlist_description = parts[1]

            continue

        if not playlist_ref:
            if not playlist_name:
                raise CommandError(
                    "A playlist name was not given and it was not found " +
                    "in the file either. Can't continue."
                )
            else:
                playlist_ref, currenttracks = get_playlist(api, playlist_name)
                if not playlist_ref and not dry_run:
                    sys.stderr.write('Playlist not found. Creating new.\n')
                    playlist_ref = api.create_playlist(playlist_name, description=playlist_description)
                yield f'Going to update playlist {playlist_name} ({playlist_ref})\n'

        trackinfo = list(csv.reader([input_line], quoting=csv.QUOTE_ALL))[0]

        if trackinfo[0] == 'Track' and trackinfo[1] == 'Artist':
            yield 'Skipping header.'
            continue

        search_term = f"{trackinfo[0]} {trackinfo[1]}"
        total = total + 1
        newtrackid, error_reason = search_track(api, search_term, currenttracks)
        if newtrackid:
            if not dry_run:
                # print(f"Add to {playlist_ref} song {newtrackid}")
                api.add_songs_to_playlist(playlist_ref, newtrackid)
            songs_added = songs_added + 1
        else:
            failed_tracks.append(trackinfo)
        sys.stderr.write(
            f"Searching {search_term}...{error_reason}\n"
        )

    yield f"{songs_added} songs added out of {total}. {total - songs_added} Failed."

    yield "Failed tracks:"
    for line in failed_tracks:
        yield f"  {line}"


def search_track(api, search_term, currenttracks):
    """
    Search for a track in the Google Music catalog.
    """

    try:
        results = api.search(search_term)
    except Exception as error:
        logging.exception(error)
        return None, "Search Failed"

    if len(results['song_hits']) > 0:
        newtrackid = results['song_hits'][0]['track']['storeId']

        if newtrackid in currenttracks:
            return None, "Dupe"
        else:
            return newtrackid, "OK"
    else:
        return None, "No Results"


def get_playlist(api, playlistname):
    """
    Get a playlist from Google Music, searching by name.

    Returns a tuple of the playlist and the tracks.
    """
    playlist = [
        x for x in api.get_all_user_playlist_contents() if x['name'] ==
                                                           playlistname
    ]
    currenttracks = list()

    if len(playlist) == 1:
        tracks = playlist[0]['tracks']
        currenttracks = [x['track']['storeId'] for x in tracks]

        playlist = playlist[0]['id']
        sys.stderr.write(
            f'Playlist named {playlistname} exists. It will be updated.\n'
        )
    else:
        playlist = None

    return playlist, currenttracks


@named('login')
def allaccesslogin():
    api = Mobileclient(debug_logging=False, validate=False)
    api.perform_oauth(open_browser=True)
