#-*- coding: utf-8 -*-

from __future__ import print_function
import httplib
import HTMLParser
import re
import argparse
import yaml
import sys

_headers = {'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'}

def parse_args():
    parser = argparse.ArgumentParser(description='Parses metal-tracker')
    parser.add_argument('min_id', type=int,
                        help='Id of the oldest torrent to retrieve')
    parser.add_argument('--start', type=int, default=0,
                        help='page number with which to start (default: 0)')
    parser.add_argument('-o', '--out',
                        help='file where to store the YAML result')
    return parser.parse_args()

def get_page(con, n):
    params = 'page={}'.format(n)
    con.request('POST', '/site/getupdates.html', params, _headers)
    r = con.getresponse()
    return r.read()

class Parser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.data = None
        self.new_torrent = False
        self.torrents = []
        self.min_id = 1e309

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('class') == 'update':
                self.torrents.append({'title': '', 'link': '',
                                 'id': None, 'data': {}})
                self.new_torrent = True
        elif tag == 'a' and self.new_torrent and 'href' in attrs:
            self.torrents[-1]['link'] = attrs['href']
            match_id = re.search('\d+', attrs['href'])
            if match_id:
                id = int(match_id.group(0))
                self.torrents[-1]['id'] = id
                self.min_id = min(id, self.min_id)
            self.new_torrent = False
        elif tag == 'img' and attrs.get('class') == 'updates':
                self.torrents[-1]['title'] = attrs['title']
        elif tag == 'li' and not attrs:
            self.data = []

    def handle_data(self, data):
        if self.data is not None:
            if len(self.data) < 2:
                self.data.append(data)
            if len(self.data) == 2:
                key, value = self.data
                self.torrents[-1]['data'][key.split(':')[0]] = value
                self.data = None

if __name__ == '__main__':
    args = parse_args()
    parser = Parser()
    page = args.start
    con = httplib.HTTPConnection('en.metal-tracker.com')
    while parser.min_id > args.min_id:
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
