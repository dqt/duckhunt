'''
File: duckhunt.py
Author: dougiefresh
Twitter: @dqt
Website: digitalgangster.com
Description: Searches Duck Duck Go's Hidden API and Returns List of Matching URLs

USAGE:
	python duckhunt.py -h
	python duckhunt.py -q queries.txt -m 10
'''

import requests
import urllib
import argparse
import sys
import time
import logging


# Set up a Global logging object
x = logging.getLogger("log")
x.setLevel(logging.DEBUG)

h1 = logging.FileHandler("duckduck.log")
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
h1.setFormatter(f)
h1.setLevel(logging.DEBUG)
x.addHandler(h1)

h2 = logging.StreamHandler()
h2.setLevel(logging.DEBUG)
f2 = logging.Formatter("%(levelname)s: %(message)s")
h2.setFormatter(f2)
x.addHandler(h2)


# Global debugging options
DUMP_HTML = False
DUMP_JSON = False

def querybuilder(query, next):
	x.debug("Building query from %s", query)
	p = '1'
	try:
		q = urllib.quote_plus(query)
	except Exception, err:
		x.exception(err)
		x.error("Something wrong with query string: %s", q)
		sys.exit(0)
	s = next
	o = "json"
	dc = "61"

	string = "p=" + p + "&q=" + q + "&" + s + "&o=" + o + "&dc=" + dc
	x.debug("Returning query string: %s", string)

	return string

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-q", "--queries", help="file containing queries to search",
						type=str)
	parser.add_argument("-m", "--max", help="max number of pages per query",
    					type=int)
	args = parser.parse_args()

	queryfile = args.queries
	maxi = args.max

	if not queryfile or not maxi:
		parser.print_help()
		sys.exit(0)

	x.info("Loading query file")
	try:
		with open(queryfile) as f:
			queries = f.read().splitlines()
	except Exception, err:
		x.exception(err)
		x.error("Problem opening query file")
		sys.exit(0)

	x.info("Starting search...")
	for query in queries:
		x.debug("Trying %s", query)
		returned = 0
		next = "s=0"
		while returned <= maxi:
			x.debug("Returned %d so far from this value", returned)
			x.debug("Next page string: %s", next)
			end = querybuilder(str(query), next)
			url = "https://duckduckgo.com/d.js?" + end
			x.debug("Full url is: %s", url)

			try:
				r = requests.get(url)
			except Exception. err:
				x.exception(err)
				x.error("Problem making GET request")
				sys.exit(0)

			if DUMP_HTML:
				with open("html_dump.log", "a") as f:
					f.write(r.text)

			try:
				j = r.json()
			except:
				x.warning("Hit end of useful output")
				x.info("Sleeping for 2 seconds then skipping query")
				time.sleep(2)
				break

			if DUMP_JSON:
				with open("json_dump.log", "a") as f:
					f.write(str(j))

			x.info("Finding next page value")
			x.debug("Setting last page to False")
			lastpage = False
			try:
				n = str(j[len(j)-1]['n'])
				x.debug("n is %s", n)
				next = n.split('&')[3]
				x.debug("next is %s", next)
				if next.find('s=')==-1:
					x.debug("No s= value, setting lastpage True")
					lastpage = True
			except:
				x.warning("No s= value, setting lastpage True")
				lastpage = True

			limit = len(j) - 2
			if lastpage:
				limit = len(j) - 1

			x.info("Writing found urls to file")
			for i in range(0, limit):
				with open("output.txt", "a") as f:
					line = str(j[i]['c'])
					f.write(line+"\n")

			returned+=1
			if lastpage:
				break

if __name__ == '__main__':
	x.info("Starting program...")
	main()
	x.info("Ending program...")
	sys.exit(1)
