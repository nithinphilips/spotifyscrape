#!/usr/bin/python
from gmusicapi import Mobileclient
from pprint import pprint
import re, sys
import argparse
import csv
import fileinput
import os.path
import codecs

parser = argparse.ArgumentParser(description='Exports a Spotify playlist to stdout or csv.')
parser.add_argument('--username', default='')
parser.add_argument('--password', default='')
parser.add_argument('--dry-run', default=False, action='store_true')
parser.add_argument('playlist')


arguments = parser.parse_args()

api = Mobileclient(False, False)
logged_in = api.login(arguments.username, arguments.password)

if not logged_in:
    sys.stderr.write('Error. Unable to login to Google Music.\n')

if arguments.playlist.lower().endswith('.csv'):
    arguments.playlist = arguments.playlist[:-4]

# 1. See if the playlist already exists.
playlist = [x for x in api.get_all_user_playlist_contents() if x['name'] == arguments.playlist]
currenttracks = list()

if len(playlist) == 1:
    tracks = playlist[0]['tracks']
    currenttracks = [x['track']['storeId'] for x in tracks]

    playlist = playlist[0]['id']
    sys.stderr.write('Playlist found. It will be updated.\n')
else:
    sys.stderr.write('Playlist not found. Creating new.\n')
    playlist = api.create_playlist(arguments.playlist)




sys.stderr.write('Will update playlist {0} ({1})\n'.format(arguments.playlist, playlist))

failed_tracks = list()
songs_added = 0
total = 0

playlist_file  = "{0}.csv".format(arguments.playlist)

if os.path.isfile(playlist_file):
    stream = open(playlist_file, "rb")
    sys.stderr.write('A file matching the playlist name was found. It will used instead of STDIN.\n')
else:
    stream = sys.stdin

for kw in stream:
    kw = re.sub('\r\n', '', kw)

    x = list(csv.reader([kw], quoting=csv.QUOTE_ALL))[0]

    if x[0] == 'Track' and x[1] == 'Artist':
        sys.stderr.write('Skipping header.\n')
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
                if not arguments.dry_run:
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

print "{0} songs added out of {1}. {2} Failed.".format(songs_added, total, total-songs_added)

print "Failed tracks:"
for line in failed_tracks:
    print "  ", line

#  div = document.getElementById('overlay');
#  div.parentElement.removeChild(div);
