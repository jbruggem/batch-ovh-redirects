#!/usr/bin/python

from SOAPpy import WSDL
import json
import pprint as pp



def main():
	soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')

	config = json.load(open('config.json', 'r'))
	domain = config['domain']

	redirects = process_redirects(json.load(open('redirects.json', 'r')), domain)


	#login
	session = soap.login(config["login"], config["password"], 'fr', 0)
	print "login successfull"

	soapExisting = soap.redirectedEmailList(session, domain)[0]

	existing = []
	for red in soapExisting:
		# print '"' + red.local+'": "'+red.target+'",'
		existing.append((u''+red.local, u''+red.target))

	new_redirects = [r for r in redirects if r not in existing]
	stale_redirects = [r for r in existing if r not in redirects]

	print
	print "Redirects to create"
	print "======================"
	pr(new_redirects)

	# TODO: add them.
		#redirectedEmailAdd
		#soap.redirectedEmailAdd(session, domain, 'staff-ribambelle', 'robin@28eme.be', '', 0)
		#print "redirectedEmailAdd successfull"

	print
	print "Redirects to remove"
	print "======================"
	pr(stale_redirects)


	# TODO: make backup dump of removed redirects
	# TODO: remove them.



	#logout
	soap.logout(session)
	print "logout successfull"


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

main()