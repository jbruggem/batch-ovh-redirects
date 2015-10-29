#!/usr/bin/python

from utils import *
import argparse
import os.path
import sys
import re
from ovhwrapper import OvhConnect


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

    # no connection needed
    if "graph" == args.action:
        graph(domain, redirects_file_path)
    # connection needed (get, set)
    else:
        with OvhConnect(config['login'], config['password'], domain) as api:

            if "get" == args.action:
                get_redirects(api, domain, redirects_file_path)

            elif "set" == args.action:
                set_redirects(api, domain, redirects_file_path)


#################
# action: get_redirects
#################

def get_redirects(api, domain, redirects_file):
    existing = api.list()

    with open(redirects_file, 'w') as f:
        f.write(json.dumps(redirects2dict(existing, domain), sort_keys=True, indent=4))


#################
# action: set_redirects
#################

def set_redirects(api, domain, redirects_file):
    existing = api.list()

    redirects = read_redirects(domain, redirects_file)

    new_redirects = [r for r in redirects if r not in existing]
    stale_redirects = [r for r in existing if r not in redirects]

    print("\nRedirects to create")
    print("======================")
    pr(new_redirects)

    print("\nRedirects to remove")
    print("======================")
    pr(stale_redirects)

    print("Do you wish the apply these changes ?")
    yes_or_exit()

    for r in new_redirects:
        api.add(r[0], r[1])

    for r in stale_redirects:
        api.remove(r[0], r[1])


#################
# action: graph
#################

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

        return '    "%s" -> "%s";\n' % red

    contents = [line(r) for r in redirects]
    ranks = '{ rank=same; "%s" }\n' % '" "'.join(externals)

    with open(graph_file, 'w') as f:
        f.write("digraph { \n     rankdir=LR; \n")
        f.writelines(contents)
        f.writelines(ranks)
        f.write('}')


if __name__ == "__main__":
    main()
