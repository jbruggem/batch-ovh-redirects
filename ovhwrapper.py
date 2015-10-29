from SOAPpy import WSDL
from SOAPpy import Types
import time


class OvhConnect:
    def __init__(self, l, p, d):
        self.domain = d
        self.login = l
        self.password = p

    def __enter__(self):
        self.soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')
        self.session = self.soap.login(self.login, self.password, 'fr', 0)
        print("login successfull")
        return OvhRedirectsApi(self.soap, self.session, self.domain)

    def __exit__(self, type, value, traceback):
        print("\n\nLogging out...")
        self.soap.logout(self.session)
        print("logout successfull")


class OvhRedirectsApi:

    def __init__(self, soap, session, domain):
        self.domain = domain
        self.session = session
        self.soap = soap

    @staticmethod
    def _wrap_call(call):
        try:
            print("Waiting...")
            time.sleep(10)
            return call()
        except Types.faultType as e:
            print("\nERROR: "+e.faultstring+"\n")

    def add(self, origin, destination):
        def call():
            return self.soap.redirectedEmailAdd(self.session, self.domain, origin, destination, '', 0)

        return self._wrap_call(call)

    def remove(self, origin, destination):
        def call():
            return self.soap.redirectedEmailDel(self.session, self.domain, origin, destination, '', 0)

        return self._wrap_call(call)

    def list(self):
        soap_existing = self.soap.redirectedEmailList(self.session, self.domain)[0]

        existing = []
        for red in soap_existing:
            existing.append((u''+red.local, u''+red.target))

        return existing