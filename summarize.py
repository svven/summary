"""
Parses a list of URLs, performs data extraction,
and renders the output in HTML format as news articles.
"""

def render(template, **kwargs):
	"""
	Renders the HTML containing provided summaries.

	The summary has to be an instance of summary.Summary, 
	or at least contain similar properties: title, image, url,
	description and collections: titles, images, descriptions.
	"""
	import jinja2

	loader = jinja2.FileSystemLoader(searchpath="templates")
	env = jinja2.Environment(loader=loader)
	temp = env.get_template(template)

	return temp.render(**kwargs)


def extract(url):
	"""
	Downloads the page from URL and calls extraction.
	Returns the Extracted instance with filtered results.

	TODO:
	Download just the HTML <head> tag first, load it
	into extractor and see if Extracted data is complete.
	Otherwise download the HTML <body> as well and load
	it into extractor passing the appropriate techniques.
	"""
	import extraction, requests
	extractor = extraction.Extractor(techniques=
		["extraction.techniques.FacebookOpengraphTags",
		 "extraction.techniques.HeadTags"])

	page = requests.get(url, timeout=10)
	page.raise_for_status()
	summary = extractor.extract(page.text, source_url=page.url)
	summary.source = url # to be removed

	return summary


def summarize(urls):
	"""
	Calls extract for each of the URLs,
	Returns the list of Extracted instances as summaries, 
	the result of the process, and the speed.
	"""
	import time

	fails = 0
	err = lambda e: e.__class__.__name__

	summaries = []
	start = time.time()
	for url in urls:
		try:
			summary = extract(url)
			print "-> %s" % url
		except KeyboardInterrupt:
			break
		except Exception, e:
			fails += 1
			summary = {
				'titles': ["[%s]" % err(e)],
				'urls': [url],
				'descriptions': [str(e)],
				'source': url,
				}
			print "[%s] (%s): %s" % (err(e), e, url)
		summaries.append(summary)
		end = time.time()

	result = fails and "Fails: %s out of %s." % (fails, len(summaries)) \
		or "Success: %s." % len(summaries)
	print result

	duration = end - start
	speed = "%.2f" % (duration/len(summaries))

	return summaries, result, speed


if __name__ == '__main__':
	urls = []
	with open('urls.txt', 'r') as file:
		urls.extend([url.strip() for url in file])

	summaries, result, speed = summarize(urls)
	page = render(template="news.html",
		summaries=summaries, result=result, speed=speed)

	with open('news.html', 'w') as file:
		file.write(page.encode('utf-8'))

