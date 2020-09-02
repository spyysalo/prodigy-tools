#!/usr/bin/env python

import os
import sys
import json
import random

from argparse import ArgumentParser


def argparser():
    ap = ArgumentParser()
    ap.add_argument('-p', '--sample-prob', type=float, default=None)
    ap.add_argument('text', nargs='+')
    return ap


def output(text, id_):
    data = {
        'text': text,
        'meta': { 'source': id_ },
    }
    print(json.dumps(data))


def process(fn, options):
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            id_ = '{}.{}'.format(os.path.splitext(os.path.basename(fn))[0], ln)
            output(l, id_)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.text:
        if args.sample_prob is not None and random.random() > args.sample_prob:
            continue
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
