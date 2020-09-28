#!/usr/bin/env python

import os
import sys
import json
import html
import random

from argparse import ArgumentParser


def argparser():
    ap = ArgumentParser()
    ap.add_argument('-t', '--text-only', default=False, action='store_true',
                    help='include "text" instead of "html" in JSONL')
    ap.add_argument('-p', '--sample-prob', type=float, default=None)
    ap.add_argument('text', nargs='+')
    return ap


def output(id_, before, text, after, options):
    before, text, after = [html.escape(t) for t in (before, text, after)]
    data = {}
    if options.text_only:
        data['text'] = text
    else:
        data['html'] = '<p class="before-context">{}</p><p>{}</p><p class="after-context">{}</p>'.format(before, text, after)
    data['meta'] = { 'source': id_ }
    print(json.dumps(data))


def process(fn, options):
    ids, texts = [], []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            id_ = '{}.{}'.format(os.path.splitext(os.path.basename(fn))[0], ln)
            ids.append(id_)
            texts.append(l)
    for i in range(len(texts)):
        id_ = ids[i]
        before = texts[i-1] if i > 0 else '-DOCSTART-'
        text = texts[i]
        after = texts[i+1] if i < len(texts)-1 else '-DOCEND-'
        output(id_, before, text, after, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.text:
        if args.sample_prob is not None and random.random() > args.sample_prob:
            continue
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
