Import Spotify Playlist into Google Play All Access
===================================================

1. Find the Playlist in the Spotify App.
2. Select all the tracks and right click on them.
3. Click on Copy Spotify URI to copy the tracks' unique identifies to clipboard.

    A Spotify track URI will look like:

        spotify:track:3dNcq4dzEtbFUM4PGeHHXp

4. Save the track URIs to a text file.
5. Run `export.py` script to get the track details:

        ./export.py tracks.txt --csv

6. The Track Name, Artist Name and Album Name will be saved to `tracks.csv`
7. Run `music.py` scipt to create a playlist in Google Play All Access.

        ./music.py [--username "joe@gmail.com" --password "DeviceSpecificPassword"] "Cool Playlist"

   `music.py` will look for `Cool Playlist.csv` in the same directory. If it doesn't exist, it will read from STDIN.

   You can also chain both commands together:

        ./export.py tracks.txt | ./music.py --username "joe@gmail.com" --password "DeviceSpecificPassword" "Cool Playlist"

8. The script will search for songs by title and artist name and add all the
   ones it can find to the playlist. Tracks that were not found for any reason
   will be listed at the end, so you can try to manually find them.

9. Enjoy!

Spotify export script inspired by <https://gist.github.com/durden/3901616>

