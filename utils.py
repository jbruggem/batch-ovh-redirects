#!/usr/bin/env python3

import sys
import json


def find_final_dests(hops, redirects, sources):
    useable_hops = [h for h in hops if h in sources]
    if len(useable_hops) == 0:
        return hops

    new_hops = set([r[1] for r in redirects if r[0] in useable_hops])
    final_destinations = [h for h in hops if h not in sources]
    return find_final_dests(new_hops.union(final_destinations), redirects, sources)

def flatten_redirects(redirects):
    sources = set([r[0] for r in redirects])
    # for each source, list of final dests
    redirects_per_source = [(s, find_final_dests([s], redirects, sources)) for s in sources]
    # flatten
    return [line for src in redirects_per_source for line in [(src[0], target) for target in src[1]]]


def read_redirects(domain, redirects_file):
    return dict2redirects(json.load(open(redirects_file, 'r')), domain)


def yes_or_exit():
    answer = input("[y/n] ")
    if answer.lower() != "y":
        sys.exit(1)


def remove_domain(email, domain):
    domain = '@'+domain
    if domain in email:
        email = email.replace(domain, '')
    return email


def append_domain(email, domain):
    if not '@' in email:
        email += "@"+domain
    return email


def pr(reds):
    for r in reds:
        print("%s => %s " % r)


def dict2tuple(red):
    return red['from'], red['to']


# turn json format (easy to write)
# into a more systematic format (easy to process)
# i.e, break up the 1 => N relationships into a list of 1 => 1
# also, append domain name for emails without a domain
def dict2redirects(rs, domain):
    reds = []
    for src in rs:
        if isinstance(rs[src], list):
            for dest in rs[src]:
                reds.append((src, dest))
        else:
            reds.append((src, rs[src]))

    return [(append_domain(r[0], domain), append_domain(r[1], domain)) for r in reds]


def redirects2dict(redirects, domain):
    res = {}
    for r in redirects:
        dest = remove_domain(r['to'], domain)
        src = remove_domain(r['from'], domain)
        try:
            res[src].append(dest)
        except KeyError:
            res[src] = [dest]
    for k in res:
        if 1 == len(res[k]):
            res[k] = res[k][0]
    return res
