#-*- coding: utf-8 -*-

from __future__ import print_function
import httplib
import HTMLParser
import re
import argparse
import yaml
import sys

_MT_ADDR = 'en.metal-tracker.com'
_HEADERS = {'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'}

def parse_args():
    """
    Parses CLI args.
    """
    parser = argparse.ArgumentParser(description='Parses metal-tracker')
    parser.add_argument('min_id', type=int,
                        help='Id of the oldest torrent to retrieve')
    parser.add_argument('--start', type=int, default=0,
                        help='page number with which to start (default: 0)')
    parser.add_argument('-o', '--out',
                        help='file where to store the YAML result')
    return parser.parse_args()

def get_page(con, n):
    """
    Returns the raw html nth page of updates using the given
    connection.
    """
    params = 'page={}'.format(n)
    con.request('POST', '/site/getupdates.html', params, _HEADERS)
    r = con.getresponse()
    return r.read()

class Parser(HTMLParser.HTMLParser):
    """
    HTML parser for metal-tracker updates. Parses torrents name, link,
    id and metadata. Adds all torrents to a torrent list.
    """
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self._data = None
        self._new_torrent = False
        self.torrents = []
        self._ids = set()

    def has_parsed(self, id):
        """
        Returns True iff id has already been parsed (i.e. oldest
        torrent parsed is older than the one referred by id).
        """
        return self._ids and min(self._ids) <= id

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('class') == 'update':
                self.torrents.append({'title': '', 'link': '',
                                 'id': None, 'data': {}})
                self._new_torrent = True
        elif tag == 'a' and self._new_torrent and 'href' in attrs:
            self.torrents[-1]['link'] = 'http://' + _MT_ADDR + attrs['href']
            match_id = re.search('\d+', attrs['href'])
            if match_id:
                id = int(match_id.group(0))
                self._ids.add(id)
                self.torrents[-1]['id'] = id
            self._new_torrent = False
        elif tag == 'img' and attrs.get('class') == 'updates':
                self.torrents[-1]['title'] = attrs['title']
        elif tag == 'li' and not attrs:
            self._data = []

    def handle_data(self, data):
        if self._data is not None:
            if len(self._data) < 2:
                self._data.append(data)
            if len(self._data) == 2:
                key, value = self._data
                self.torrents[-1]['data'][key.split(':')[0]] = value
                self._data = None

if __name__ == '__main__':
    args = parse_args()
    parser = Parser()
    page = args.start
    con = httplib.HTTPConnection(_MT_ADDR)
    while not parser.has_parsed(args.min_id):
        print('Parsing page {}'.format(page), file=sys.stderr)
        content = get_page(con, page).decode('utf8')
        parser.feed(content)
        page += 1
    torrents = [t for t in parser.torrents if t["id"] > args.min_id]

    if args.out:
        with open(args.out, 'w') as f:
            yaml.dump(torrents, f)
    else:
        yaml.dump(torrents, sys.stdout)
