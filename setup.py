#!/usr/bin/env python
# -*- coding: utf8 -*-

import setuptools


setuptools.setup(
    name="autotorrent",
    version="1.0",
    packages=setuptools.find_packages(),
    zip_safe=True,
    author="Simon Marti",
    author_email="simon@ceilingcat.ch",
    description="Automated downloader for TV series",
    keywords="automatic tv series torrent download",
    install_requires=("requests", "lxml", "beautifulsoup4", "tweepy")
)
