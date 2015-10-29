#!/usr/bin/python

from SOAPpy import WSDL
import json
import argparse
import os.path
import sys
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["get", "set", "graph"])
    parser.add_argument("-r", "--redirects", default="redirects.json")
    parser.add_argument("-c", "--config", default="config.json")
    args = parser.parse_args()

    redirects_file_path = os.path.abspath(args.redirects)
    if "get" == args.action and os.path.isfile(redirects_file_path):
        print(redirects_file_path)
        print("Redirects file exists and will be overwritten. Are you sure ?")
        yes_or_exit()

    if args.action in ["set", "graph"] and not os.path.isfile(redirects_file_path):
        print(redirects_file_path)
        print("Redirects file does not exist. Cannot continue.")
        sys.exit(1)

    config = json.load(open('config.json', 'r'))
    domain = config['domain']

    if "graph" == args.action:
        graph(domain, redirects_file_path)
    else:
        login = config['login']
        password = config['password']
        with OvhConnect(login, password) as (soap, session):
            soap_existing = soap.redirectedEmailList(session, domain)[0]

            existing = []
            for red in soap_existing:
                existing.append((u''+red.local, u''+red.target))

            if "get" == args.action:
                get_redirects(existing, redirects_file_path)
            elif "set" == args.action:
                set_redirects(domain, existing, redirects_file_path)


def graph(domain, redirects_file):
    # ensure we remove the @28eme domain everywhere for the graph
    redirects = read_redirects(domain, redirects_file)
    redirects = [(remove_domain(r[0], domain), remove_domain(r[1], domain)) for r in redirects]

    graph_file = re.sub(r"\.json$", '.dot', redirects_file)
    if graph_file == redirects_file:
        print redirects_file
        print graph_file
        raise Exception("Error")

    externals = []

    def line(red):
        if '@' in red[0]:
            externals.append(red[0])

        if '@' in red[1]:
            externals.append(red[1])

        return '    "%s" -- "%s";\n' % red

    contents = [line(r) for r in redirects]
    ranks = '{ rank=same, "%s" }\n' % '", "'.join(externals)

    with open(graph_file, 'w') as f:
        f.write("graph { \n     rankdir=LR; \n")
        f.writelines(contents)
        f.writelines(ranks)
        f.write('}')


def get_redirects(existing, redirects_file):
    with open(redirects_file, 'w') as f:
        f.write(json.dumps(dict(existing), sort_keys=True, indent=4))


def set_redirects(domain, existing, redirects_file):
    redirects = read_redirects(domain, redirects_file)

    new_redirects = [r for r in redirects if r not in existing]
    stale_redirects = [r for r in existing if r not in redirects]

    print("\nRedirects to create")
    print("======================")
    pr(new_redirects)

    # TODO: add them.
        #redirectedEmailAdd
        #soap.redirectedEmailAdd(session, domain, 'staff-ribambelle', 'robin@28eme.be', '', 0)
        #print "redirectedEmailAdd successfull"

    print("\nRedirects to remove")
    print("======================")
    pr(stale_redirects)

    # TODO: make backup dump of removed redirects
    # TODO: remove them.


def read_redirects(domain, redirects_file):
    return process_redirects(json.load(open(redirects_file, 'r')), domain)


class OvhConnect:
    def __init__(self, l, p):
        self.login = l
        self.password = p

    def __enter__(self):
        self.soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')
        self.session = self.soap.login(self.login, self.password, 'fr', 0)
        print("login successfull")
        return self.soap, self.session

    def __exit__(self, type, value, traceback):
        print("\n\nLogging out...")
        self.soap.logout(self.session)
        print("logout successfull")


def yes_or_exit():
    answer = raw_input("[Y/N]")
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
         print( r[0] + " => " + r[1] )


def process_redirects(rs, domain):
    reds = []
    for src in rs:
        if isinstance(rs[src], list):
            for dest in rs[src]:
                reds.append((src, dest))
        else:
            reds.append((src, rs[src]))

    reds = [ (r[0], append_domain(r[1], domain)) for r in reds]

    return reds


if __name__ == "__main__":
    main()
