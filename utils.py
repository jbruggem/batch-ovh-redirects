import sys
import json


def read_redirects(domain, redirects_file):
    return dict2redirects(json.load(open(redirects_file, 'r')), domain)


def yes_or_exit():
    answer = raw_input("[y/n] ")
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


# turn json format (easy to write)
# into a more systematic format (easy to process)
# i.e, break up the 1 => N relationships into a list of 1 => 1
# also, append domain name for dests without a domain
def dict2redirects(rs, domain):
    reds = []
    for src in rs:
        if isinstance(rs[src], list):
            for dest in rs[src]:
                reds.append((src, dest))
        else:
            reds.append((src, rs[src]))

    return [(r[0], append_domain(r[1], domain)) for r in reds]


def redirects2dict(redirects, domain):
    res = {}
    for r in redirects:
        dest = remove_domain(r[1], domain)
        try:
            res[r[0]].append(dest)
        except KeyError:
            res[r[0]] = [dest]
    for k in res:
        if 1 == len(res[k]):
            res[k] = res[k][0]
    return res
