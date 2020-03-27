# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('spotifyscrape/spotifyscrape.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "spotifyscrape",
    packages = ["spotifyscrape"],
    package_data = {"spotifyscrape" : ["*.conf"]},
    install_requires=[
        "argcomplete",
        "argh",
        "gmusicapi",
        "spotipy",
    ],
    entry_points = {
        "console_scripts": [
            'spotifyscrape = spotifyscrape.spotifyscrape:main',
            ]
        },
    version = version,
    description = "Application to convert Spotify Playlists to Google Play All Access Playlists.",
    long_description = long_descr,
    author = "Nithin Philips",
    author_email = "nithin@nithinphilips.com",
    url = "",
    )
