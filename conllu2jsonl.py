#!/usr/bin/env python

# Get sentence text and ID from CoNLL-U data and format as JSONL

import sys
import json
import random

from argparse import ArgumentParser


ID_LINE_START = '# sent_id = '

TEXT_LINE_START = '# text = '


def argparser():
    ap = ArgumentParser()
    ap.add_argument('-p', '--sample-prob', type=float, default=None)
    ap.add_argument('conllu', nargs='+')
    return ap


def output(text, id_, fn, ln, options):
    if (options.sample_prob is not None and
        random.random() > options.sample_prob):
        return
    if text is None:
        raise ValueError('{} line {}: missing text'.format(fn, ln))
    if id_ is None:
        raise ValueError('{} line {}: missing id for text "{}"'.format(
            fn, ln, text))
    data = {
        'text': text,
        'meta': { 'source': id_ },
    }
    print(json.dumps(data))


def process(fn, options):
    text, id_ = None, None
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l.isspace() or not l:
                output(text, id_, fn, ln, options)
                text, id_ = None, None
            elif l.startswith(ID_LINE_START):
                if id_ is not None:
                    raise ValueError('{} line {}: dup ID'.format(fn, ln))
                id_ = l[len(ID_LINE_START):]
            elif l.startswith(TEXT_LINE_START):
                if text is not None:
                    raise ValueError('{} line {}: dup text'.format(fn, ln))
                text = l[len(TEXT_LINE_START):]


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.conllu:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
