#-*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import yaml
import sys
import re

import IPython

def parse_args():
    """
    Parses CLI args.
    """
    desc = str('Browses metal-tracker. Enters in an IPython shell '
               'with following variables defined: torrents, index.')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input',
                        help='file where to fetch the YAML list of torrents')
    return parser.parse_args()

def get_values(torrents, key):
    """
    Returns all the different values for the metadata key in torrents.
    """
    return set(t['data'][key] for t in torrents if key in t['data'])

def get_keys(torrents):
    """
    Returns all the different metadata keys in torrents.
    """
    return set(sum([t['data'].keys() for t in torrents], []))

def make_index(torrents, keys, simplify=True):
    """
    Makes a recursive index of the torrents with the given list of
    keys. If simplify is True (default) then when a subindex contains
    only one value for the given key, it doesn't create a subindex but
    rather a list.
    """
    if not keys:
        return torrents
    index, key = {}, keys.pop()
    for t in torrents:
        k = t['data'].get(key)
        if k not in index:
            index[k] = [t]
        else:
            index[k].append(t)
    for k in index:
        new_index = make_index(index[k], list(keys))
        if type(new_index) is not dict or len(new_index) > 1:
            index[k] = new_index
        else:
            index[k] = new_index.values()[0]
    return index

def get_regex(bands_list):
    """
    Makes a regex which match all bands in bands_list.
    """
    return re.compile('(' + ')|('.join(bands_list) + ')', flags=re.IGNORECASE)

def filter_torrents(torrents, regex):
    """
    Filter torrents with a regex on title.
    """
    return [t for t in torrents if regex.match(t['title'])]

if __name__ == '__main__':
    args = parse_args()
    with open(args.input) as f:
        print('Loading torrents from {}'.format(args.input), file=sys.stderr)
        torrents = yaml.load(f)
    index = make_index(torrents, ['Year', 'Country', 'Style', 'Format'])
    IPython.embed()
