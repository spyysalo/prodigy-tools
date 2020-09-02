#!/usr/bin/env python

# Convert key data from Prodigy JSONL to simple TSV format

import sys
import json

from datetime import datetime
from argparse import ArgumentParser
from logging import warning


def argparser():
    ap = ArgumentParser()
    ap.add_argument('jsonl', nargs='+')
    ap.add_argument('--dataset', default=None)
    return ap


def normalize_space(text):
    return text.replace('\t', ' ').replace('\n', ' ')


def output(id_, text, user, created, accepted, fn, ln):
    try:
        id_ = normalize_space(id_)
        text = normalize_space(text)
        if user is None:
            user = str(user)
        user = normalize_space(user)
        if created is None:
            created = str(created)
        created = normalize_space(created)
        if not accepted:
            accepted = None
        else:
            accepted = ','.join(accepted)
        print('{}\t{}\t{}\t{}\t{}'.format(id_, user, created, accepted, text))
    except:
        raise ValueError('{} line {}: {} {} {}'.format(
            fn, ln, id_, text, accepted))


def get_annotator(data, options):
    session = data['_session_id']
    if 'annotator' in data:
        return data['annotator']    # Explicitly included
    if options.dataset is None or session is None:
        return session    # Can't figure out which part is user
    elif session.startswith(options.dataset):
        return session[len(options.dataset)+1:]
    else:
        warning('dataset ({}) does not match session ({})'.format(
            options.dataset, session))
        return session


def get_created(data, date_only=False):
    created = data.get('created')
    if created is None:
        return None
    elif not date_only:
        return created
    else:
        created = datetime.fromisoformat(created)    # Python 3.7
        return str(created.date())


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
            annotator = get_annotator(data, options)
            created = get_created(data)
            output(id_, text, annotator, created, accepted, fn, ln)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.jsonl:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
