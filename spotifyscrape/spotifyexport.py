#!/usr/bin/env python

# NOTE: Idea for this script came from:
# spotify-export (https://github.com/jlund/spotify-export)

import csv
import re
import sys
import logging
import spotipy
import spotipy.util as util
from argh import *

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

def csv_write_header(writer):
    writer.writerow(["Track", "Artist", "Album"])

def write_tracks(results, writer):
    for tracks in results['items']:
        track = tracks['track']
        csv_write_track(writer, track)

def csv_write_track(writer, track):
    title = track['name'].encode('utf8')
    album = track['album']['name'].encode('utf8')
    artist = track['artists'][0]['name'].encode('utf8')

    writer.writerow([title, artist, album])

@arg('username', help='Your Spotify user name')
@arg('uri', help='The Public HTTP URL to a playlist')
@named('export-playlist')
def exportplaylist(uri, username):
    """
    Given a Spotify playlist's public HTTP URL, prints the track Title, Artist and Album.

    The URL must be in the format:
     http://open.spotify.com/user/<user-id>/playlist/<playlist-id>

    The first line of the output will tbe playlist's name as a comment.
    """

    scope = 'user-library-read'
    pattern = "http://open.spotify.com/user/([^/]+)/playlist/(.+)"

    match = re.match(pattern, uri)
    if match:
        username = match.group(1)
        playlistid = match.group(2)
    else:
        raise CommandError("Cannot read the URI. See the help for expected format.")

    sys.stderr.write("Searching for {}'s playlist {}\n".format(username, playlistid))

    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist(username, playlistid, fields="name,tracks,next")
    sys.stdout.write("# Playlist: {}\n".format( results['name']))

    csv_write_header(writer)

    tracks = results['tracks']
    write_tracks(tracks, writer)
    while tracks['next']:
        tracks = sp.next(tracks)
        write_tracks(tracks, writer)
