import argparse
import os.path
import re
import sys
from collections import OrderedDict
from itertools import groupby

from ovhwrapper import OvhConnect
from utils import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["get", "set", "list", "graph"])
    parser.add_argument("-r", "--redirects", default="redirects.json")
    parser.add_argument("-c", "--config", default="config.json")
    parser.add_argument("-d", "--dry-run", action="store_true")
    parser.add_argument("-f", "--flatten-redirects", action="store_true")
    args = parser.parse_args()

    redirects_file_path = os.path.abspath(args.redirects)

    if args.action in ["set", "graph"] and not os.path.isfile(redirects_file_path):
        print(redirects_file_path)
        print("Redirects file does not exist. Cannot continue.")
        sys.exit(1)

    config = json.load(open("config.json"))
    domain = config["domain"]

    # no connection needed
    if args.action == "graph":
        graph(domain, redirects_file_path, args.dry_run)
    elif args.action == "list":
        view_list(domain, redirects_file_path)
    # connection needed (get, set)
    else:
        with OvhConnect(
            domain,
            config["app_key"],
            config["app_secret"],
            config["consumer_key"],
        ) as api:
            if args.action == "get":
                get_redirects(api, domain, redirects_file_path, args.dry_run)

            elif args.action == "set":
                set_redirects(
                    api,
                    domain,
                    redirects_file_path,
                    args.flatten_redirects,
                    args.dry_run,
                )


#################
# action: get_redirects
#################


def get_redirects(api, domain, redirects_file, dry_run):
    existing = api.list()
    json_content = json.dumps(
        redirects2dict(existing, domain),
        sort_keys=True,
        indent=4,
    )

    if dry_run:
        print(json_content)
        print("\nDry run, not writing redirects file.")
        return

    if os.path.isfile(redirects_file):
        print(redirects_file)
        print("Redirects file exists and will be overwritten. Are you sure ?")
        yes_or_exit()

    with open(redirects_file, "w") as f:
        f.write(json_content)


#################
# action: set_redirects
#################


def set_redirects(api, domain, redirects_file, flat_redirects, dry_run):
    existing = api.list()
    existing_tuples = [dict2tuple(r) for r in existing]

    redirects = read_redirects(domain, redirects_file)

    if flat_redirects:
        expected_redirects = flatten_redirects(redirects)
    else:
        expected_redirects = redirects

    new_redirects = [r for r in expected_redirects if r not in existing_tuples]
    stale_redirects = [r for r in existing if dict2tuple(r) not in expected_redirects]

    if len(new_redirects) > 0:
        print("\nRedirects to create")
        print("======================")
        display_redirects(new_redirects)

    if len(stale_redirects) > 0:
        print("\nRedirects to remove")
        print("======================")
        display_redirects([dict2tuple(r) for r in stale_redirects])

    if len(new_redirects) == 0 and len(stale_redirects) == 0:
        print("\nNothing to do, Redirects are up to date!\n")
        return

    if dry_run:
        print("\n Dry run, not applying changes.")
        return

    if flat_redirects:
        print("""\nYou asked to flatten redirects. This means that you will not be
able to rebuild the redirects graph locally by doing a 'get' from the server.
It also means you loose the ability to manually configure an alias easily
using OVH's UI.

Are you sure you wish to proceed  ?""")
        yes_or_exit()

    print("\nDo you wish the apply these changes ?")
    yes_or_exit()

    for r in new_redirects:
        print("api add %s => %s" % r)
        resp = api.add(r[0], r[1])
        print(resp)

    for r in stale_redirects:
        print("api remove %s => %s " % dict2tuple(r))
        resp = api.remove(r["id"])
        print(resp)


#################
# action: list
#################


def view_list(domain, redirects_file):
    redirects = read_redirects(domain, redirects_file)

    def print_redir(redir):
        print(redir[0] + " => " + str(redir[1]))

    print("\nExternal: \n================\n")
    [print_redir(r) for r in redirects if not r[1].endswith("@" + domain)]

    print("\nInternal: \n================\n")
    internals = [r for r in redirects if r[1].endswith("@" + domain)]
    grouped_internals = [
        [g[0], list(map(lambda x: x[1], g[1]))]
        for g in groupby(internals, lambda x: x[0])
    ]
    [print_redir(r) for r in grouped_internals]


#################
# action: graph
#################


def graph(domain, redirects_file, dry_run):
    # ensure we remove the main domain everywhere for the graph
    redirects = read_redirects(domain, redirects_file)
    redirects = [
        (remove_domain(r[0], domain), remove_domain(r[1], domain)) for r in redirects
    ]

    graph_file = re.sub(r"\.json$", ".dot", redirects_file)
    if graph_file == redirects_file:
        print(redirects_file, graph_file)
        raise Exception("Error: trying to write graph in redirects file.")

    def is_external(red):
        ret = set()

        if "@" in red[0]:
            ret.add(red[0])

        if "@" in red[1]:
            ret.add(red[1])

        return ret

    def line(red):
        return '    "%s" -> "%s" [fillcolor=gray, color=gray];\n' % red

    # flatmap & remove duplicates
    all_nodes = list(OrderedDict.fromkeys([r for pairs in redirects for r in pairs]))

    # extract externals
    externals = [node for node in all_nodes if "@" in node]
    normals = [node for node in all_nodes if "@" not in node]

    config_nodes_normal = [
        '    "'
        + n
        + '"  [shape=box,style=rounded,label="'
        + n
        + '",fontcolor=darkgreen, color=darkgreen]; \n'
        for n in normals
    ]
    config_nodes_external = [
        '    "'
        + n
        + '"  [shape=plaintext,label="'
        + n
        + '",fontcolor=darkslategray4]; \n'
        for n in externals
    ]
    vertices = [line(r) for r in redirects]
    ranks = '{ rank=same; "%s" }\n' % '" "'.join(externals)

    if dry_run:
        print("\nDry run, not writing to graph file: " + graph_file + ".")
        return

    with open(graph_file, "w") as f:
        f.write("digraph { \n     rankdir=LR; \n")
        f.writelines(vertices)
        f.writelines(config_nodes_normal)
        f.writelines(config_nodes_external)
        f.writelines(ranks)
        f.write("}")


if __name__ == "__main__":
    main()
