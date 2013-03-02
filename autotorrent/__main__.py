# -*- coding: utf8 -*-
import optparse
import os.path
import sys
import webbrowser

import autotorrent


usage = ("Usage: %prog [options] [series [series [...]]]")
parser = optparse.OptionParser(usage=usage, prog="autotorrent")
parser.add_option("-f", "--series-file", dest="series_file", metavar="<file>",
                  default=None, help="File containing a list of series"
                  " (one per line)")
parser.add_option("-s", "--storage", dest="storage", metavar="<file>",
                  default=[], action="append",
                  help="Directory containing already downloaded episodes")
parser.add_option("-o", "--open", dest="open",
                  default=False, action="store_true",
                  help="Open found magnet links in a browser")
parser.add_option("-t", "--transmission", dest="transmission", metavar="<url>",
                  default=None, help="URL of a transmission web-interface")
parser.add_option("-v", "--verbose", dest="verbose",
                  default=False, action="store_true",
                  help="Verbose output")

(opts, args) = parser.parse_args()
series_list = args

if opts.series_file is not None:
    if not os.path.isfile(opts.series_file):
        parser.error("This file does not exist: %s" % opts.series_file)
    with open(opts.series_file) as f:
        for line in f:
            if line.strip():
                series_list.append(line.strip())

for folder in opts.storage:
    if not os.path.exists(folder):
        parser.error("This directory does not exist: %s" % folder)

if not series_list:
    parser.error("You have to provide at least one series")

if not opts.storage:
    parser.error("You have to provide at least one storage location")

storage = autotorrent.Storage(opts.storage)
verbose = opts.verbose
magnets = []

for series_name in series_list:
    try:
        series = autotorrent.Series(series_name)
        missing_episodes = list(storage.missing_episodes(series))
        if verbose:
            if missing_episodes:
                print ("Series '%s' is missing %s episodes of season %s: %s" %
                       (series, len(missing_episodes),
                        missing_episodes[0].season,
                        ", ".join(str(episode.episode) for episode
                                  in missing_episodes)))
            else:
                print "There are no new episode for series '%s'" % series
        for episode in missing_episodes:
            magnet = episode.magnet_link()
            if magnet is None:
                sys.stderr.write(
                    "Couldn't find a suitable torrent for %s\n" % episode
                )
            else:
                magnets.append(magnet)
    except Exception as e:
        sys.stderr.write("Refreshing series '%s' failed: %s\n" %
                         (series, e.message))

if opts.open:
    def download(magnet):
        webbrowser.open(magnet, new=2, autoraise=False)
elif opts.transmission is not None:
    try:
        transmission = autotorrent.Transmission(opts.transmission)
    except Exception as e:
        sys.stderr.write(e.message)
        sys.stderr.write("\n")
        sys.exit(1)
    download = transmission.add_torrent
else:
    def download(magnet):
        print magnet

for magnet in magnets:
    download(magnet)
