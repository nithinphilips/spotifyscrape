# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""Export a Spotify playlist to CSV"""

import csv
import re
import spotipy
import sys
import io

from argh import arg, named, CommandError, aliases

from .config import read_config
from .spotipyutil import prompt_for_user_token

SPOTIFY_API_SCOPE = 'user-library-read'
USERNAME_ARG = arg(
    '--username',
    help='Your Spotify user name',
    default=read_config().get("Spotify", "username")
)
CLIENT_ID_ARG = arg(
    '--client-id',
    default=read_config().get("Spotify", "client-id")
)
CLIENT_SECRET_ARG = arg(
    '--client-secret',
    default=read_config().get("Spotify", "client-secret")
)
REDIRECT_URI_ARG = arg(
    '--redirect-uri',
    default=read_config().get("Spotify", "redirect-uri")
)

@arg('tracklist', help="A text file containing the Spotify track URIs.")
@named('export-tracks')
def exporttracks(tracklist):
    """
    Given a list of Spotify track URIs, prints the track Title, Artist and
    Album.

    Expected input is in this format:

        spotify:track:1oVlMEQe8myOjNCASaAHnQ
        spotify:track:0zoHzM4bKGQ8Q6wze334Qs
        spotify:track:4p2olbKKjXCdJmR4Xa1mYv

    The input file should have one item per line. Blank lines are OK. Invalid
    items will be skipped.
    """

    spotify = spotipy.Spotify()
    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    csv_write_header(writer)
    failed = 0
    tracks = None

    with open(tracklist, 'r') as tracklistfile:
        lines = [line.strip() for line in tracklistfile.readlines()]
        lines = [line for line in lines if line and len(line) > 0]

        tracks = spotify.tracks(lines)['tracks']

    for track in tracks:
        if track:
            csv_write_track(writer, track)
        else:
            failed = failed + 1

    sys.stderr.write(
        f"{len(lines)} tracks processed. {len(tracks) - failed} found. {failed} failed.\n"
    )


def check_required_arg(argument, name):
    """Check if a required argument is present. If not raise an exception"""
    if not argument:
        raise CommandError(
            f"{name} must be provided as either command-line argument or in the"
            "application configuration file."
        )


@named("login")
@USERNAME_ARG
@CLIENT_ID_ARG
@CLIENT_SECRET_ARG
@REDIRECT_URI_ARG
def checktoken(username=None, client_id=None, client_secret=None,
               redirect_uri=None):
    """Login to Spotify or refresh the authorization token."""

    check_required_arg(username, "Username")
    check_required_arg(client_id, "Client ID")
    check_required_arg(client_secret, "Client Secret")
    check_required_arg(redirect_uri, "Redirect URL")

    token = prompt_for_user_token(
        username, scope=SPOTIFY_API_SCOPE,
        client_id=client_id, client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    if token:
        return "Token OK."
    else:
        return "Unable to get token."

@USERNAME_ARG
@CLIENT_ID_ARG
@CLIENT_SECRET_ARG
@REDIRECT_URI_ARG
@arg('uri', help='The Public HTTP URL to a playlist')
@aliases('export-playlist')
@named('export')
def exportplaylist(uri, username=None, client_id=None, client_secret=None,
                   redirect_uri=None):
    """
    Given a Spotify playlist's URI, prints the track Title, Artist and Album.

    The URL must be in one of these formats:
     http://open.spotify.com/user/<user-id>/playlist/<playlist-id>
     http://open.spotify.com/playlist/<playlist-id>
     spotify:user:<user-id>:playlist:<playlist-id>

    You need to be authorized before you can use this command. See the README
    for details.
    """

    check_required_arg(username, "Username")
    check_required_arg(client_id, "Client ID")
    check_required_arg(client_secret, "Client Secret")
    check_required_arg(redirect_uri, "Redirect URL")

    pattern = "http://open.spotify.com/user/([^/]+)/playlist/(.+)"
    pattern2 = "https://open.spotify.com/playlist/(.+)"
    alt_pattern = "spotify:user:([^:]+):playlist:(.+)"

    match = re.match(pattern, uri)
    if not match:
        match = re.match(alt_pattern, uri)

    match2 = re.match(pattern2, uri)

    if match:
        playlist_username = match.group(1)
        playlistid = match.group(2)
        open_spotify_uri = f"http://open.spotify.com/user/{playlist_username}/playlist/{playlistid}"
    elif match2:
        playlist_username = None
        playlistid = match2.group(1)
        open_spotify_uri = f"http://open.spotify.com/playlist/{playlistid}"
    else:
        raise CommandError(
            "Cannot read the playlist URI. See the help for expected format."
        )

    sys.stderr.write(
        f"Searching for {playlist_username}'s playlist {playlistid}\n"
    )

    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)

    token = prompt_for_user_token(
        username, scope=SPOTIFY_API_SCOPE,
        client_id=client_id, client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    spotify = spotipy.Spotify(auth=token)
    if playlist_username:
        results = spotify.user_playlist(
            playlist_username, playlistid, fields="name,tracks,next"
        )
    else:
        results = spotify.playlist(
            playlistid, fields="name,tracks,next"
        )

    sys.stdout.write(f"# Playlist: {results['name']}\n")
    sys.stdout.write(f"# Description: from {open_spotify_uri}\n")

    csv_write_header(writer)

    tracks = results['tracks']
    csv_write_tracks(writer, tracks)
    while tracks['next']:
        tracks = spotify.next(tracks)
        csv_write_tracks(writer, tracks)

def csv_write_header(writer):
    """Writes the header row in CSV format"""
    writer.writerow(["Track", "Artist", "Album"])

def csv_write_tracks(writer, tracks):
    """Writes a list of tracks in CSV format"""
    for trackitem in tracks['items']:
        track = trackitem['track']
        csv_write_track(writer, track)

def csv_write_track(writer, track):
    """Writes a single track in CSV format"""
    title = track['name']
    album = track['album']['name']
    artist = track['artists'][0]['name']

    writer.writerow([title, artist, album])
