#!/usr/bin/env python

# Convert key data from Prodigy JSONL to simple TSV format

import sys
import json

from argparse import ArgumentParser
from logging import warning


def argparser():
    ap = ArgumentParser()
    ap.add_argument('jsonl', nargs='+')
    return ap


def normalize_space(text):
    return text.replace('\t', ' ').replace('\n', ' ')


def output(id_, text, accepted, fn, ln):
    try:
        id_ = normalize_space(id_)
        text = normalize_space(text)
        if not accepted:
            accepted = None
        else:
            accepted = ','.join(accepted)
        print('{}\t{}\t{}'.format(id_, accepted, text))
    except:
        raise ValueError('{} line {}: {} {} {}'.format(
            fn, ln, id_, text, accepted))


def process(fn, options):
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            data = json.loads(l)
            answer = data.get('answer')
            if answer != 'accept':
                warning('{} line {}: skip answer {}'.format(fn, ln, answer))
                continue
            # Assume source attribute is used as an ID (convention)
            id_ = data['meta']['source']
            text = data['text']
            accepted = data['accept']
            output(id_, text, accepted, fn, ln)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.jsonl:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
