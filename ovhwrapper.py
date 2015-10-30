import os
import ovh
import pickle

CACHE_FILE = 'cache.pickle'

class OvhConnect:
    def __init__(self, dom, appkey, secret, conskey):
        self.conskey = conskey
        self.secret = secret
        self.appkey = appkey
        self.dom = dom

    def __enter__(self):
        self.client = ovh.Client(
            endpoint='ovh-eu',
            application_key=self.appkey,
            application_secret=self.secret,
            consumer_key=self.conskey,
        )
        print("login successfull")
        return OvhRedirectsApi(self.dom, self.client)

    def __exit__(self, type, value, traceback):
        pass


class OvhRedirectsApi:
    def __init__(self, domain, client):
        self.client = client
        self.domain = domain
        self.cached_redirects = {}
        self.read_cache()

    def add(self, origin, destination):
        return self.client.post('/email/domain/%s/redirection' % self.domain,
                                _from=origin,
                                to=destination,
                                localCopy=False)

    def read_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                self.cached_redirects = pickle.load(f)['redirects']

    def write_cache(self):
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump({'redirects': self.cached_redirects}, f)

    def get(self, id):
        if id in self.cached_redirects:
            return self.cached_redirects[id]
        else:
            red = self.fetch(id)
            self.cached_redirects[red['id']] = red
            self.write_cache()
            return red

    def fetch(self, id):
        print("fetching non-cached redirect %s " % id)
        return self.client.get('/email/domain/%s/redirection/%s' % (self.domain, id))

    def remove(self, id):
        return self.client.delete('/email/domain/%s/redirection/%s' % (self.domain, id))

    def list(self):
        print("asking for redirs id list...")
        ids = self.client.get('/email/domain/%s/redirection' % self.domain)
        print("asking for redirects for each id...")
        list = [self.get(id) for id in ids]

        return list

