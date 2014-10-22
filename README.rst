Spotify Scrape
==============
SpotifyScrape exports playlists (private and publicly shared) from Spotify and
imports them into Google Play Music All Access.

The tool exports playlists from Spotify to a CSV format that contains the track
Title, Artist name and Album name. The ``import`` command reads the CSV file
and creates the copy of the playlist in All Access.

Commands
--------
export-tracks
    Given a list of Spotify track URIs, retrieves the track Title, Artist and
    Album.

    This method does not require any authentication. However, you will need to
    use the Spotify desktop client to get the Spotify URI (the one that looks
    like ``spotify:track:3HaYLn3KGQ6PF7O3TbhNat``)

export-playlist
    Given a Spotify playlist's public HTTP URL, prints the track Title, Artist
    and Album. You need to be authorized before you can use this command. You
    can export your private playlists and any other users' public playlists.

checktoken
    Retrieves or refreshes Spotify authorization token.

import
    Imports a playlist into Google Play Music All Access.

Import Spotify Playlist into Google Play All Access
---------------------------------------------------
This method requires authorization.

1. First, register for a Spotify developer key at
   https://developer.spotify.com/my-applications

   You will need a free Spotify account.

2. Add the URI ``http://localhost`` to the Redirect URI whitelist.
3. Create a configuration file ``.spotifyscrape`` in your home directory with
   the following content::

    [All Access]
    username = <your-username>
    password = <your-password>
    [Spotify]
    username = <your-username>
    client-id = <your-client-id>
    client-secret = <your-client-secret>
    redirect-uri = http://localhost

   Replace the place holders with actual values. If you use two-factor
   authentication with your Google account, generate a new `App password
   <https://support.google.com/accounts/answer/185833?hl=en>`_.

5. Check the Token::

    spotifyscrape checktoken

   You will see something like::

        User authentication requires interaction with your
        web browser. Once you enter your credentials and
        give authorization, you will be redirected to
        a url.  Paste that url you were directed to to
        complete the authorization.

        Please navigate here: https://accounts.spotify.com/authorize?scope=user-library-read&redirect_uri=...

        Enter the URL you were redirected to:

6. Copy and paste the URL
   ``https://accounts.spotify.com/authorize?scope=user-library-read&redirect_uri=...``
   into your browser. Login to Spotify and authorize the app.
7. You will be redirected to a page that looks like an error page. The
   information required to complete the authorization is in the URL.
8. Copy the URL of the page and paste it back in the terminal and press Enter
9. If everything went correctlu, you will see *Token OK*
10. Grab a playlist::

        spotifyscrape export-playlist http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp

    You will see::

        # Playlist: Hipsterlicious September 2014
        "Track","Artist","Album"
        "Back In The Days","Splendid","Back In The Days"
        "Too Straight","Island Boy","Basic Instincts"
        "Ghosts","Alagoas","Ghosts"
        ....

    You don't need to run this command every time. You can export the playlist
    and import it into All Access in one step. See the next step for details.

11. Next, upload to Google Play All Access::

        spotifyscrape export-playlist http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp | spotifyscrape import

12. The script will create or update the playlist in All Access.

The script adds tracks to the All Access playlist by searching by the track
title and artist name. It's not fool proof and not all track will match.

Installation/Setting Up VirtualEnv
----------------------------------
1. Clone the repository::

    git clone https://github.com/nithinphilips/spotifyscrape.git
    cd SpotifyScrape

2. Create the VirtualEnv::

    virtualenv venv
    source venv/bin/activate

3. Install SpotifyScrape and dependencies::

    python setup.py install
