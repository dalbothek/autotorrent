# -*- coding: utf8 -*-
import re
import os
import urllib2
import json

import requests
import bs4


BLOCK_FILES = ("www.Torrentday.com.txt",)


class Episode(object):
    def __init__(self, series, season, episode):
        self.series = series
        self.season = season
        self.episode = episode

    def magnet_link(self):
        torrent = PirateBaySearch(self).best_result()
        if torrent is not None:
            return torrent.magnet

    def __repr__(self):
        return "%s S%02dE%02d" % (self.series, self.season, self.episode)

    def __eq__(self, other):
        return (isinstance(other, Episode) and self.series == other.series and
                self.season == other.season and self.episode == other.episode)


class Series(object):
    SERIES_INFO_URL = "http://services.tvrage.com/tools/quickinfo.php"
    LATEST_EPISODE_PATTERN = re.compile("\nLatest Episode@(\d{2})x(\d{2})\\^")

    def __init__(self, name):
        self.name = name
        self._latest_episode = None

    @property
    def latest_episode(self):
        if self._latest_episode is None:
            r = requests.get(self.SERIES_INFO_URL, params={
                'show': self.name.replace(" ", "+")
            })
            if not r.ok:
                r.raise_for_status()
            match = self.LATEST_EPISODE_PATTERN.search(r.content)
            if match is None:
                raise Exception("Series '%s' doesn't exist" % self)
            season, episode = match.groups()
            self._latest_episode = Episode(self, int(season), int(episode))
        return self._latest_episode

    def __str__(self):
        return self.name


class Storage(object):
    EPISODE_PATTERN = re.compile("S(\d{2})E(\d{2})", flags=re.IGNORECASE)
    NORMALIZE_PATTERN = re.compile("[^\w\d]+")

    def __init__(self, paths):
        if isinstance(paths, basestring):
            paths = (paths,)
        self.files = [self._normalize(entry) for entry
                      in sum((os.listdir(path) for path in paths), [])
                      if self.EPISODE_PATTERN.search(entry) is not None]

    def _normalize(self, entry):
        return self.NORMALIZE_PATTERN.sub(" ", entry.lower())

    def existing_episodes(self, series, season=None):
        series_name = self._normalize(series.name)
        duplicates = []
        for entry in self.files:
            if series_name in entry:
                e_season, episode = self.EPISODE_PATTERN.search(entry).groups()
                if season is None or season == int(e_season):
                    episode = Episode(series, int(e_season), int(episode))
                    if episode not in duplicates:
                        yield episode
                        duplicates.append(episode)

    def missing_episodes(self, series, season=None):
        season = season or series.latest_episode.season
        existing_episodes = sorted(
            self.existing_episodes(series, season=season),
            key=lambda e: e.episode
        )
        i = 1
        for episode in existing_episodes:
            if episode.episode > i:
                for j in xrange(i, episode.episode):
                    yield Episode(series, season, j)
            i = episode.episode + 1
        if i <= series.latest_episode.episode:
            for j in xrange(i, series.latest_episode.episode + 1):
                yield Episode(series, season, j)


class PirateBaySearch(object):
    SEARCH_URL = "http://thepiratebay.se/search/%s/0/99/208"
    MAX_FILE_COUNT = 5

    def __init__(self, episode):
        self.results = []
        r = requests.post(self.SEARCH_URL % urllib2.quote(repr(episode)))
        if not r.ok:
            r.raise_for_status()
        doc = bs4.BeautifulSoup(r.content, "lxml")
        content = doc.body.find("div", id="content")
        rows = content("tr")[2:]
        for row in rows:
            links = row("td")[1]("a")
            url = links[0].get("href")
            magnet = links[1].get("href")
            seeders = int(row("td")[2].text)
            self.results.append(
                self.PirateBaySearchResult(episode, url, magnet, seeders)
            )

    def best_result(self):
        for result in sorted(self.results, key=lambda r: -r.seeders):
            if (not result.contains_blocked_files() and
                    result.file_count() <= self.MAX_FILE_COUNT):
                return result

    class PirateBaySearchResult(object):
        BASE_URL = "http://thepiratebay.se"
        FILE_LIST_URL = BASE_URL + "/ajax_details_filelist.php"

        def __init__(self, episode, url, magnet, seeders):
            self.episode = episode
            self.url = self.BASE_URL + url
            self.magnet = magnet
            self.seeders = seeders
            self.id_ = int(url[9:url.find("/", 9)])

        def __repr__(self):
            return "%s (%s seeders)" % (self.episode, self.seeders)

        def file_count(self):
            r = requests.post(self.url)
            if not r.ok:
                r.raise_for_status()
            doc = bs4.BeautifulSoup(r.content, "lxml")
            return int(doc.find("div", id="details").dl("dd")[1].a.text)

        def contains_blocked_files(self):
            r = requests.post(self.FILE_LIST_URL, params={'id': self.id_})
            if not r.ok:
                r.raise_for_status()
            doc = bs4.BeautifulSoup(r.content, "lxml")
            for td in doc("td", align="left"):
                if td.text in BLOCK_FILES:
                    return True
            return False


class Transmission(object):
    TIMEOUT = 5

    def __init__(self, url):
        if not url.endswith("/rpc"):
            if not url.endswith("/"):
                url += "/"
            url += "transmission/rpc"
        if not url.startswith("http"):
            url = "http://" + url
        self.url = url
        self.session_id = None
        self._renew_session_id()

    def _request(self, data, raw_response=False):
        headers = {"x-transmission-session-id": self.session_id}
        try:
            r = requests.post(self.url, headers=headers, data=json.dumps(data),
                              timeout=self.TIMEOUT)
        except:
            return None if raw_response else False
        return r if raw_response else r.ok

    def _renew_session_id(self):
        r = self._request({"method": "get-session"}, raw_response=True)
        if r is None:
            raise Exception("Can't connect to transmission server")
        if (r.status_code == requests.codes.conflict and
                'x-transmission-session-id' in r.headers):
            self.session_id = r.headers['x-transmission-session-id']
        else:
            raise Exception("Unable to establish session")

    def add_torrent(self, url):
        return self._request({"method": "torrent-add",
                              "arguments": {"filename": url,
                                            "paused": False}})
