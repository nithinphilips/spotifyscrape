# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# shows a user's playlists (need to be authenticated via oauth)

import os
import sys
import subprocess
from spotipy import oauth2
import spotipy

TOKEN_CACHE_PATH = os.path.expanduser("~/.spotify-oauth")

def prompt_for_user_token(username, scope=None, client_id=None, client_secret=None, redirect_uri=None):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app

    '''


    if not os.path.exists(TOKEN_CACHE_PATH):
        os.makedirs(TOKEN_CACHE_PATH)

    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not client_id:
        sys.stderr.write('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:

            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

            Get your credentials at
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    cache_path = os.path.join(TOKEN_CACHE_PATH, ".cache-" + username)

    sp_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri,
        scope=scope, cache_path=cache_path
    )

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        sys.stderr.write('''

            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.

        ''')
        auth_url = sp_oauth.get_authorize_url()
        try:
            subprocess.call(["open", auth_url])
            sys.stderr.write("Opening {} in your browser\n".format(auth_url))
        except:
            try:
                subprocess.call(["cygstart", auth_url])
                sys.stderr.write(
                    "Opening {} in your browser\n".format(auth_url)
                )
            except:
                sys.stderr.write("Please navigate here: {}\n".format(auth_url))

        sys.stderr.write("\n\n")
        response = raw_input("Enter the URL you were redirected to: ")
        sys.stderr.write("\n\n")
        sys.stderr.write("\n\n")

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None
