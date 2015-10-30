Batch update mail redirections using OVH management APIs.

Env: 

* runtime: tested with python 3.4
* Dependencies: OVH


# OVH

First, go there to get app key and app secret: 

Then, run the following code:
```python
import ovh
c = ovh.Client(endpoint='ovh-eu', application_key=KEY, application_secret=SECRET)
c.request_consumerkey(access_rules = [
       {'method': 'POST', 'path': '/email/domain/'},
       {'method': 'GET', 'path': '/email/domain/'}, 
       {'method': 'PUT', 'path': '/email/domain/'}, 
       {'method': 'DELETE', 'path': '/email/domain/'}
   ])
```

The reply to this request will be a consumer key and an URL. Visit the URL with your browser to validate the consumer key.

Refs:

* [https://api.ovh.com/g934.first_step_with_api]
* [https://github.com/ovh/python-ovh]
* [https://api.ovh.com/createToken/index.cgi?GET=/me]


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
