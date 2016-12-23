Spotify Scrape
==============
**Spotify Scrape** exports playlists from Spotify_ and imports them into
`Google Play Music All Access`_. This tool is not approved or authorized by
either Spotify or Google. Use it at your own risk.

Getting Started
---------------
Install Python 2.7. Download the source and install::

    git clone https://github.com/nithinphilips/spotifyscrape.git
    cd SpotifyScrape
    python setup.py install

Usage
-----
Spotify Scrape is run using one of these commands::

    spotifyscrape <command>

Here are the supported commands:

Export Tracks
~~~~~~~~~~~~~

Usage: ``spotifyscrape export-tracks <tracklist>``

Gets the track Title, Artist and Album from a list of Spotify track URIs.

This method does not require any authentication. However, you will need to use
the Spotify desktop client to get the Spotify URI (the one that looks like
``spotify:track:3HaYLn3KGQ6PF7O3TbhNat``). You can right click on a track to
get the URI.

Example::

    $ cat tracks.txt
    spotify:track:1oVlMEQe8myOjNCASaAHnQ
    spotify:track:0zoHzM4bKGQ8Q6wze334Qs
    spotify:track:4p2olbKKjXCdJmR4Xa1mYv

    $ spotifyscrape export-tracks tracks.txt
    "Track","Artist","Album"
    "The Bad In Each Other","Feist","Metals"
    "Graveyard","Feist","Metals"
    "Caught A Long Wind","Feist","Metals"
    3 tracks processed. 3 found. 0 failed.

Export Playlist
~~~~~~~~~~~~~~~
Usage: ``spotifyscrape export-playlist <URI>``

Gets all the tracks in a Spotify playlist.

You need to have a Spotify Developer API key before you can use this command.
You can export your own private playlists and other users' public playlists.

Example::

    $ spotifyscrape export-playlist spotify:user:1150884627:playlist:3cyD3zInBW4j97ay6xB2WQ
    Searching for 1150884627's playlist 3cyD3zInBW4j97ay6xB2WQ
    # Playlist: Beach Bar Boutique-Vol8
    # Description: from http://open.spotify.com/user/1150884627/playlist/3cyD3zInBW4j97ay6xB2WQ
    "Track","Artist","Album"
    "Lighting The Spark","Dave Sparkz","Ivory Lounge"
    "Hello Sunshine","Damien Jurado","Hello Sunshine"
    "Feel Like I Do","Disclosure","Moog For Love"
    "Taxi Bossa","FloFilz","Cenário"
    ...

Check Token
~~~~~~~~~~~
Usage: ``spotifyscrape checktoken``

Updates the Spotify API token. You must run this command at least once before
using the ``export-playlist`` command.

Example::

    $ spotifyscrape checktoken
    Token OK.

Import
~~~~~~
Usage: ``spotifyscrape import --playlist <tracks-file>`` or ``cat <tracks-file>
| spotifyscrape import``

Imports a playlist into *Google Play Music All Access*.

This command expects a list of track in ``STDIN``. Alternatively, you can pass
a track list file name using the ``--playlist`` argument.

The track list input format is same as the output of the ``export-playlist``
command.

If a line starts with ``# Playlist:``, then the rest of the line will be used
as the playlist name. If the line starts with ``# Description:``  the remainder
will be used as the playlist description.

We match tracks in the input by searching by the *track* and *artist* name in
the Google Play All Access library. A match is not always guaranteed. You might
especially run into issues with remixes and covers.

Example::

    $ cat tracks.csv
    # Playlist: Beach Bar Boutique-Vol8
    # Description: from http://open.spotify.com/user/1150884627/playlist/3cyD3zInBW4j97ay6xB2WQ
    "Track","Artist","Album"
    "Lighting The Spark","Dave Sparkz","Ivory Lounge"
    "Hello Sunshine","Damien Jurado","Hello Sunshine"

    $ cat tracks.csv | spotifyscrape import
    Playlist not found. Creating new.
    Going to update playlist Beach Bar Boutique-Vol8 (47ca4a0c-b717-43c1-bf51-c50bcf25b3d3)

    Skipping header.
    Searching Lighting The Spark Dave Sparkz...OK
    Searching Hello Sunshine Damien Jurado...OK
    ...
    33 songs added out of 38. 5 Failed.
    Failed tracks:
    ['Mission & 24th', 'Pimp Rekker', 'Om: Hip Hop Soul Sessions']
    ['Forever This', 'Fries', 'Norman Jay MBE presents GOOD TIMES 30th Anniversary Edition']
    ...

One time Setup
--------------
1. First, register for a Spotify developer key at
   https://developer.spotify.com/my-applications

   You will need a free Spotify account.

   Once registered, click on *Create an App*. Give it a name and description.

   In the *Redirect URIs* section, add the URI ``http://localhost``.

2. Create a configuration file ``.spotifyscrape`` in your home directory with
   the following content::

    [All Access]
    username = you@gmail.com
    password = <your-password>
    [Spotify]
    username = you@facebook.com
    client-id = <your-client-id>
    client-secret = <your-client-secret>
    redirect-uri = http://localhost

   Replace the place holders with actual values. If you use two-factor
   authentication with your Google account, generate a new `App password
   <https://support.google.com/accounts/answer/185833?hl=en>`_.

3. Update the Spotify API token::

    $ spotifyscrape checktoken

   You will see something like::

        User authentication requires interaction with your
        web browser. Once you enter your credentials and
        give authorization, you will be redirected to
        a url.  Paste that url you were directed to to
        complete the authorization.

        Please navigate here: https://accounts.spotify.com/authorize?...

        Enter the URL you were redirected to:

   Copy and paste the URL ``https://accounts.spotify.com/authorize?...`` into
   your browser. Login to Spotify and authorize the app.

   You will be redirected to a page that looks like an error page. The
   information required to complete the authorization is in the URL.

   Copy the URL of the page and paste it back in the terminal and press Enter

   If everything went correctly, you will see *Token OK*

Import a Playlist
-----------------
Download the playlist and upload to Google Play All Access::

    spotifyscrape export-playlist http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp | spotifyscrape import

or using the ``spotify:`` URI::

    spotifyscrape export-playlist spotify:user:1150884627:playlist:3cyD3zInBW4j97ay6xB2WQ | spotifyscrape import

The playlist will be created in All Access.

License
-------
.. code::

    Spotify Scrape. Import Spotify playlists to Google Play Music
    All Access.
    Copyright (C) 2016 Nithin Philips

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

.. _Google Play Music All Access: https://play.google.com/music/listen
.. _Spotify: https://www.spotify.com/
