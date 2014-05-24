"""
Parses a list of urls, performs data extraction,
and renders the output in html format as news articles.
"""

def render(articles, template):
	"""
	Renders the html containing provided articles.

	The article has to be an instance of extraction.Extracted, 
	or at least contain similar properties: title, image, url,
	description and collections: titles, images, descriptions.
	"""
	import jinja2

	loader = jinja2.FileSystemLoader(searchpath="templates")
	env = jinja2.Environment(loader=loader)
	temp = env.get_template(template)

	return temp.render(articles=articles)


def extract(url):
	"""
	Downloads the page from url and calls extraction.
	Returns the Extracted instance with filtered results.

	TODO:
	Download just the html <head> tag first, load it
	into extractor and see if Extracted data is complete.
	Otherwise download the html <body> as well and load
	it into extractor passing the appropriate techniques.
	"""
	import extraction, requests
	extractor = extraction.Extractor()

	page = requests.get(url, timeout=10)
	page.raise_for_status()
	article = extractor.extract(page.text, source_url=page.url)
	article.source = url # to be removed

	return article


def summarize(urls, template="news.html"):
	"""
	Calls extract for each of the urls,
	and renders the output in news articles format, if not 
	otherwise specified by the template.
	"""
	fails = 0
	err = lambda e: e.__class__.__name__
	articles = []

	for url in urls:
		try:
			article = extract(url)
			print "-> %s" % url
		except Exception, e:
			fails += 1
			article = {
				'titles': ["[%s]" % err(e)],
				'urls': [url],
				'descriptions': [str(e)],
				'source': url
				}
			print "[%s] (%s): %s" % (err(e), e, url)
		articles.append(article)
	print "Fails: %s out of %s." % (fails, len(urls))

	return render(articles, template)


if __name__ == '__main__':
	urls = []
	with open('urls.txt', 'r') as file:
		urls.extend([url.strip() for url in file])
	page = summarize(urls)
	with open('news.html', 'w') as file:
		file.write(page.encode('utf-8'))

