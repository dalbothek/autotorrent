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
    -v, --verbose                    Verbose output

## Example:
    $ python -m autotorrent -s ~/Downloads -t http://localhost:9091 "The Big Bang Theory" "New Girl"

**Attention:** Depending on what country you're living in downloading and/or seeding torrents might be illegal.
