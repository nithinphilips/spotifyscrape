Import Spotify Playlist into Google Play All Access
===================================================

1. Create an Application at https://developer.spotify.com/my-applications/#!/applications
2. Add the URI ``http://localhost`` to the Redirect URI whitelist.
3. Create a configuration file ``.spotifyscrape`` in your home directory with the following contents::

    [All Access]
    username = <your-username>
    password = <your-password>
    [Spotify]
    username = <your-username>
    client-id = <your-client-id>
    client-secret = <your-client-secret>
    redirect-uri = http://localhost


4. Find a playlist URL. Eg ``http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp``
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


6. Copy and paste ``https://accounts.spotify.com/authorize?scope=user-library-read&redirect_uri=...`` into your browser. Login and authorize the app.
7. You will be redirected to a page that looks like an error page. 
8. Copy the URL of the page and paste it back in the terminal and press Enter
9. You will see *Token OK*
10. Grab the playlist::

        spotifyscrape export-playlist http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp

    You will see::

        # Playlist: Hipsterlicious September 2014
        "Track","Artist","Album"
        "Back In The Days","Splendid","Back In The Days"
        "Too Straight","Island Boy","Basic Instincts"
        "Ghosts","Alagoas","Ghosts"
        ....

11. Upload to Google Play All Access::

        spotifyscrape export-playlist http://open.spotify.com/user/115683679/playlist/55RoVrmRtlgMF0kZnco4vp | spotifyscrape import

12. The script will create or update the playlist in All Access.
