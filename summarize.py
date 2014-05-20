# -*- coding: utf-8 -*-
"""
Parses a list of urls, performs data extraction,
and renders the output in html format as news articles.
"""


def render(articles, template):
	"""
	Renders the html containing provided articles.

	The article has to be an instance of extraction.Extracted, 
	or at least contain similar properties: title, image, url,
	description and lists/tuples titles, images, descriptions.
	
	Feeds are not rendered at the moment - might be discarded.
	(That's the best added value of this nice little library.)
	"""
	import jinja2

	loader = jinja2.FileSystemLoader(searchpath="templates")
	env = jinja2.Environment(loader=loader)
	temp = env.get_template(template)

	return temp.render(articles=articles)


def extract(urls):
	"""
	Parses each url and performs the extraction.
	Returns a list of Extracted instances aka articles.

	For now it downloads the whole page from the url in order
	to perform the extraction. It would be better to define 
	some extraction techniques that can work with fragments of
	the HTML page so we could stream the request for faster 
	processing and minimum bandwidth. Will keep this in mind.
	"""
	import urllib2, requests, extraction

	fails = 0
	err = lambda e: e.__class__.__name__

	extractor = extraction.Extractor()
	for url in urls:
		try:
			page = requests.get(url, timeout=10)
			page.raise_for_status()
			article = extractor.extract(page.text, source_url=page.url)
			article.source = url
			print "-> %s" % url
			yield article
		except Exception, e:
			fails += 1
			print "[%s] (%s): %s" % (err(e), e, url)
			article = extraction.Extracted(
				titles=["[%s]" % err(e)],
				urls=[url],
				descriptions=[str(e)],
				source=url)
			yield article
	print "Fails: %s out of %s." % (fails, len(urls))

def summarize(urls, template="news.html"):
	"""
	Main function of the module.
	Parses a list of urls, performs data extraction,
	and renders the output in html format as news articles,
	if not otherwise specified by the template.
	"""
	articles = extract(urls)
	return render(articles=articles, template=template)


if __name__ == '__main__':
	urls = []
	with open('urls.txt', 'r') as file:
		urls.extend([url.strip() for url in file])
	page = summarize(urls)
	with open('news.html', 'w') as file:
		file.write(page.encode('utf-8')


