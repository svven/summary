"""
Summary class improves extraction.Extracted by providing
incremental load mechanism, and especially image validation.

But the main difference is that it performs the requests.

Extraction is performed gradually by parsing the HTML <head>
tag first, applying specific head extraction techniques, and
goes on to the <body> only if Summary data is not complete.
"""
import extraction, requests
from contextlib import closing

CHUNK_SIZE = 1024

class Summary(object):
	"Provides incremental load mechanism and validation."

	def __init__(self, source_url=None):
		"""
		Unlike Extracted ctor, this one just sets the source_url.
		Extracted data is loaded later gradually by calling extract.
		"""
		self.source_url = source_url

		# self.title = None
		# self.description = None
		# self.image = None
		# self.url = None

		self.titles = []
		self.descriptions = []
		self.images = []
		self.urls = []

	# # Non-plural properties
		# @property
		# def title(self):
		# 	"Return the best title, if any."
		# 	if self.titles:
		# 		return self.titles[0]
		# 	else:
		# 		return None

		# @property
		# def description(self):
		# 	"Return the best description, if any."
		# 	if self.descriptions:
		# 		return self.descriptions[0]
		# 	else:
		# 		return None

		# @property
		# def image(self):
		# 	"Return the best image, if any."
		# 	if self.images:
		# 		return self.images[0]
		# 	else:
		# 		return None

		# @property
		# def url(self):
		# 	"Return the best url, if any."
		# 	if self.urls:
		# 		return self.urls[0]
		# 	else:
		# 		return None

	def _is_complete(self):
		# return False
		return self.titles and self.descriptions \
			and self.images and self.urls and True
			# self.title and self.description and self.image and self.url \

	def _load(self, titles=[], descriptions=[], images=[], urls=[], **kwargs):
		"""
		Loads extracted data into Summary.
		Performs validation and filtering on-the-fly, and sets the
		non-plural fields to the best specific item so far.
		"""
		# TODO: filter out invalid items
		self.titles.extend(titles)
		self.descriptions.extend(descriptions)
		self.urls.extend(urls)
		self.images.extend(images)

		# TODO: set non-plural fields to best item

	def _clean_url(self, url):
		"Fixes the url, but it should also discard useless query params."
		import urllib
		import urlparse
		def url_fix(s, charset='utf-8'):
		    "https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/urls.py"
		    if isinstance(s, unicode):
		        s = s.encode(charset, 'ignore')
		    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
		    path = urllib.quote(path, '/%')
		    qs = urllib.quote_plus(qs, ':&=')
		    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
		return url_fix(url)

	def _get_tag(self, response, tag_name="html"):
		"Iterates response content and returns the tag if found."
		tag_start = tag_end = None
		def find_tag(html, tag_name, tag_start, tag_end):
			if not tag_start:
				start = html.find("<%s" % tag_name)
				if start >= 0: tag_start = start
			if tag_start:
				end = html.find("</%s>" % tag_name)
				if end > tag_start: tag_end = end+len(tag_name)+3
			if tag_end: # and tag_start
				return html[tag_start:tag_end]
			return None
		for chunk in response.iter_content(CHUNK_SIZE, decode_unicode=True):
			self._html += chunk
			tag = find_tag(self._html.lower(), tag_name, tag_start, tag_end)
			if tag:
				return tag
		tag = find_tag(self._html.lower(), tag_name, tag_start, tag_end)
		return tag

	def extract(self, check_url=None):
		"""
		Downloads HTML <head> tag first, extracts data from it using
		specific head techniques, loads it and checks if is complete. 
		Otherwise downloads the HTML <body> tag as well and loads data 
		extracted by using appropriate semantic techniques.

		Eagerly calls check_url(url) if any, before parsing the HTML.
		Provided function should throw an exception to break extraction.
		E.g.: URL has been summarized before; URL points to off limits
		websites like facebook.com and so on.
		"""
		url = self.source_url
		with closing(requests.get(url, stream=True, timeout=10)) as response:
			response.raise_for_status()
			# TODO: validate content-type
			# response.headers.get('content-type')

			url = self._clean_url(response.url)
			if check_url:
				check_url(url)

			self._html = u""
			head = self._get_tag(response, tag_name="head")
			# print "Get head: %s" % len(head)
			extractor = extraction.Extractor(techniques=[
				"extraction.techniques.FacebookOpengraphTags",
		        "extraction.techniques.TwitterSummaryCardTags",
				"extraction.techniques.HeadTags"
			])
			extracted = extractor.extract(head, source_url=url)
			self._load(**extracted)

			if self._is_complete():
				return # done

			body = self._get_tag(response, tag_name="body")
			# print "Get body: %s" % len(body)
			extractor = extraction.Extractor(techniques=[
		        "extraction.techniques.HTML5SemanticTags",
		        "extraction.techniques.SemanticTags"				
			])
			extracted = extractor.extract(body, source_url=url)
			self._load(**extracted)

		# that's it

