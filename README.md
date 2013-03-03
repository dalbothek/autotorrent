# autorrent - Automated TV series downloader
This little tool helps you stay up to date on your favorite tv shows.

## Installation:
    $ git clone git://github.com/sadimusi/autotorrent.git
    $ cd autotorrent
    $ sudo python setup.py install

## Usage:
    $ python -m autotorrent [options] [series [series [...]]]

### Options
    -f <file>, --series-file=<file>  File containing a list of series (one per line)
    -s <file>, --storage=<file>      Directory containing already downloaded episodes
    -o, --open                       Open found magnet links in a browser
    -t <url>, --transmission=<url>   URL of a transmission web-interface
    --twitter=<file>                 Twitter settings created with autotorrent.twitter
    -v, --verbose                    Verbose output

## Example:
    $ python -m autotorrent -s ~/Downloads -t http://localhost:9091 "The Big Bang Theory" "New Girl"

## Twitter notifications
Autotorrent can notify you via direct message on Twitter when new shows are found. To use this feature you have to create a settings file with

    $ python -m autotorrent.twitter user [user [...]] [-f <output file>]

You can then use this file with the `--twitter` option of autotorrent.

**Attention:** Depending on what country you're living in downloading and/or seeding torrents might be illegal.
