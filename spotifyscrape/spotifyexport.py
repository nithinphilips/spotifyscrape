#!/usr/bin/env python

# NOTE: Idea for this script came from:
# spotify-export (https://github.com/jlund/spotify-export)

import csv
import logging
import os
import re
import spotipy
import sys
import spotipy.util as util

from argh import *
from .config import read_config
from .spotipyutil import prompt_for_user_token

SPOTIFY_API_SCOPE = 'user-library-read'

@arg('tracklist', help="A text file containing the Spotify track URIs.")
@named('export-tracks')
def exporttracks(tracklist):
    """Given a list of Spotify track URIs, prints the track Title, Artist and Album.

    Expected input is in this format:

        spotify:track:1oVlMEQe8myOjNCASaAHnQ
        spotify:track:0zoHzM4bKGQ8Q6wze334Qs
        spotify:track:4p2olbKKjXCdJmR4Xa1mYv

    The input file should have one item per line. Blank lines are OK. Invalid items will be skipped."""

    spotify = spotipy.Spotify()
    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    csv_write_header(writer)
    failed = 0

    with open(tracklist, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
        lines = [line for line in lines if line and len(line) > 0]

        tracks = spotify.tracks(lines)['tracks']

        for track in tracks:
            if track:
                csv_write_track(writer, track)
            else:
                failed = failed + 1

        sys.stderr.write("{0} tracks processed. {1} found. {2} failed.\n".format(len(lines), len(tracks) - failed, failed))


def check_required_arg(argument, name):
    if not argument:
        raise CommandError(
            "{} must be provided as either command-line argument or in the application configuration file.".format(name))


@arg('--username', help='Your Spotify user name', default=read_config().get("Spotify", "username"))
@arg('--client-id', default=read_config().get("Spotify", "client-id"))
@arg('--client-secret', default=read_config().get("Spotify", "client-secret"))
@arg('--redirect-uri', default=read_config().get("Spotify", "redirect-uri"))
def checktoken(username=None, client_id=None, client_secret=None, redirect_uri=None):
    """Retrieve or refresh Spotify authorization token.
    """

    check_required_arg(username, "Username")
    check_required_arg(client_id, "Client ID")
    check_required_arg(client_secret, "Client Secret")
    check_required_arg(redirect_uri, "Redirect URL")

    token = prompt_for_user_token(username, scope=SPOTIFY_API_SCOPE,
            client_id=client_id, client_secret=client_secret,
            redirect_uri=redirect_uri)

    if token:
        return "Token OK."
    else:
        return "Unable to get token."

@arg('--username', help='Your Spotify user name', default=read_config().get("Spotify", "username"))
@arg('--client-id', default=read_config().get("Spotify", "client-id"))
@arg('--client-secret', default=read_config().get("Spotify", "client-secret"))
@arg('--redirect-uri', default=read_config().get("Spotify", "redirect-uri"))
@arg('uri', help='The Public HTTP URL to a playlist')
@named('export-playlist')
def exportplaylist(uri, username=None, client_id=None, client_secret=None, redirect_uri=None):
    """
    Given a Spotify playlist's public HTTP URL, prints the track Title, Artist and Album.

    The URL must be in the format:
     http://open.spotify.com/user/<user-id>/playlist/<playlist-id>

    You need to be authorized before you can use this command. See the README for details.
    """

    check_required_arg(username, "Username")
    check_required_arg(client_id, "Client ID")
    check_required_arg(client_secret, "Client Secret")
    check_required_arg(redirect_uri, "Redirect URL")

    pattern = "http://open.spotify.com/user/([^/]+)/playlist/(.+)"

    match = re.match(pattern, uri)
    if match:
        playlist_username = match.group(1)
        playlistid = match.group(2)
    else:
        raise CommandError("Cannot read the playlist URI. See the help for expected format.")

    sys.stderr.write("Searching for {}'s playlist {}\n".format(playlist_username, playlistid))

    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)

    token = prompt_for_user_token(username, scope=SPOTIFY_API_SCOPE,
            client_id=client_id, client_secret=client_secret,
            redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist(playlist_username, playlistid, fields="name,tracks,next")
    sys.stdout.write("# Playlist: {}\n".format( results['name']))

    csv_write_header(writer)

    tracks = results['tracks']
    csv_write_tracks(tracks, writer)
    while tracks['next']:
        tracks = sp.next(tracks)
        csv_write_tracks(tracks, writer)

def csv_write_header(writer):
    writer.writerow(["Track", "Artist", "Album"])

def csv_write_tracks(results, writer):
    for tracks in results['items']:
        track = tracks['track']
        csv_write_track(writer, track)

def csv_write_track(writer, track):
    title = track['name'].encode('utf8')
    album = track['album']['name'].encode('utf8')
    artist = track['artists'][0]['name'].encode('utf8')

    writer.writerow([title, artist, album])
