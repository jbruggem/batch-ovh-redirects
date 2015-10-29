Batch update mail redirections using OVH management APIs.

* runtime: tested with python 2.7
* Dependencies: soappy


# options

```bash
usage: redirects.py [-h] [-r REDIRECTS] [-c CONFIG] {get,set,graph}
```

* `redirects` is a JSON file with the all the mapping between source and destination emails. Default: `redirects.json`. See example in repo.
* `config` is a JSON file with your OVH config: domain name, login, password.  Default: `config.json`. See example in repo.

# actions

## get

Retrieve existing mappings from OVH. Usage:

```bash
python redirects.py get
```

It will store all the existing redirections in `redirects.json`.

## set

Replace all email mappings on OVH. Usage:

```bash
python redirects.py set
```

It will use `redirects.json` to replace all the redirects by those in that file.
    

## graph

Produce a graphviz `.dot` file describing the contents of  `redirects.json`. Usage:

```bash
python redirects.py graph
```

Then you can make a PNG out of it (provided you have graphviz installed):

```bash
dot redirects.dot -Tpng -o redirects.png
```
