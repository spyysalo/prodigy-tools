#!/usr/bin/env python

# Convert key data from Prodigy JSONL to simple TSV format

import sys
import json
import html
import re

from datetime import datetime
from argparse import ArgumentParser
from logging import warning


BEFORE_CONTEXT_RE = re.compile(r'<p class="before-context">.*?</p>')

AFTER_CONTEXT_RE = re.compile(r'<p class="after-context">.*?</p>')

PARAGRAPH_RE = re.compile(r'<p>(.*)</p>')


def argparser():
    ap = ArgumentParser()
    ap.add_argument('jsonl', nargs='+')
    ap.add_argument('-f', '--mark-flagged', default=False, action='store_true')
    ap.add_argument('-i', '--include-ignore', default=False, action='store_true')
    ap.add_argument('--dataset', default=None)
    return ap


def normalize_space(text):
    return text.replace('\t', ' ').replace('\n', ' ')


def output(id_, text, user, created, accepted, flagged, fn, ln, options):
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
            label_str = 'None'
        else:
            label_str = ','.join(accepted)
        if options.mark_flagged and flagged:
            label_str += '+FLAG'
        print('{}\t{}\t{}\t{}\t{}'.format(id_, user, created, label_str, text))
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


def get_text(data):
    if 'text' in data:
        return data['text']
    else:
        text = data['html']
        # Wipe context, if any
        text = BEFORE_CONTEXT_RE.sub('', text)
        text = AFTER_CONTEXT_RE.sub('', text)
        text = PARAGRAPH_RE.sub(r'\1', text)
        text = html.unescape(text)
        return text


def process(fn, options):
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            data = json.loads(l)
            answer = data.get('answer')
            if answer == 'accept':
                accepted = data['accept']
            elif answer == 'ignore' and options.include_ignore:
                accepted = ['-IGNORE-']
            else:
                warning('{} line {}: skip answer {}'.format(fn, ln, answer))
                continue
            # Assume source attribute is used as an ID (convention)
            id_ = data['meta']['source']
            text = get_text(data)
            annotator = get_annotator(data, options)
            created = get_created(data)
            flagged = data.get('flagged', False)
            output(id_, text, annotator, created, accepted, flagged, fn, ln, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.jsonl:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
