"""
Summary class improves extraction.Extracted by providing
incremental load mechanism, and especially image validation.

But the main difference is that it performs the requests.

Extraction is performed gradually by parsing the HTML <head>
tag first, applying specific head extraction techniques, and
goes on to the <body> only if Summary data is not complete.
"""
import requests, extraction, filters
from contextlib import closing

CHUNK_SIZE = 1024 # 1 KB
GET_ALL_DATA = False # False for better performance

class Summary(object):
	"Provides incremental load mechanism and validation."

	def __init__(self, source_url=None):
		"""
		Unlike Extracted ctor, this one just sets the source_url.
		Extracted data is loaded later gradually by calling extract.
		"""
		# self.title = None
		# self.description = None
		# self.image = None
		# self.url = None

		self.titles = []
		self.descriptions = []
		self.images = []
		self.urls = []

		self.source_url = source_url
		self.clean_url = self.source_url

	# Non-plural properties
	@property
	def title(self):
		"Return the best title, if any."
		if self.titles:
			return self.titles[0]
		else:
			return None

	@property
	def description(self):
		"Return the best description, if any."
		if self.descriptions:
			return self.descriptions[0]
		else:
			return None

	@property
	def image(self):
		"Return the best image, if any."
		if self.images:
			return self.images[0]
		else:
			return None

	@property
	def url(self):
		"Return the best canonical url, or the cleaned source url."
		if self.urls:
			return self.urls[0]
		else:
			return self.clean_url


	def _is_complete(self):
		# return self.title and self.description and self.image and self.url and True
		return self.titles and self.descriptions and self.images and self.urls and True

	def _load(self, titles=[], descriptions=[], images=[], urls=[], **kwargs):
		"""
		Loads extracted data into Summary.
		Performs validation and filtering on-the-fly, and sets the
		non-plural fields to the best specific item so far.
		If GET_ALL_DATA is False, it gets only the first valid item.
		"""
		if GET_ALL_DATA or not self.titles:
			self.titles.extend(titles)
		if GET_ALL_DATA or not self.descriptions:
			self.descriptions.extend(descriptions)

		if GET_ALL_DATA or not self.urls:
			# urls = [self._clean_url(u) for u in urls]
			urls = map(self._clean_url, urls)
			self.urls.extend(urls)
		
		if GET_ALL_DATA:
			# images = [i for i in [self._filter_image(i) for i in images] if i] 
			images = filter(None, map(self._filter_image, images))
			self.images.extend(images)
		elif not self.images:
			for i in images:
				image = self._filter_image(i)
				if image:
					self.images.append(image)
					break

		# TODO: set non-plural fields to best item by sorting
		# self.descriptions = sorted(self.descriptions, key = lambda t: len(t), reverse=True)

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

	def _filter_image(self, url):
		"The param is the image URL, which is returned if it passes all the filters."
		return reduce(lambda f, g: f and g(f), 
		[
			filters.AdblockURLFilter()(url),
			filters.NoImageFilter(),
			filters.SizeImageFilter(),
			filters.MonoImageFilter(),
			filters.FormatImageFilter(),
		])
	
	def _get_tag(self, response, tag_name="html"):
		"Iterates response content and returns the tag if found."
		lower_html = self._html.lower()
		tag_start = tag_end = None
		def find_tag(html, tag_name, tag_start, tag_end):
			if not tag_start:
				start = html.find("<%s" % tag_name)
				if start >= 0: tag_start = start
			if tag_start:
				end = html.find("</%s>" % tag_name)
				if end > tag_start: tag_end = end+len(tag_name)+3
			if tag_end: # and tag_start
				return self._html[tag_start:tag_end]
			return None
		for chunk in response.iter_content(CHUNK_SIZE, decode_unicode=True):
			self._html += chunk
			lower_html += chunk.lower()
			tag = find_tag(lower_html, tag_name, tag_start, tag_end)
			if tag:
				return tag
		tag = find_tag(lower_html, tag_name, tag_start, tag_end)
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
		with closing(requests.get(self.clean_url, stream=True, timeout=10)) as response:
			response.raise_for_status()
			# TODO: validate content-type
			# response.headers.get('content-type')

			self.clean_url = self._clean_url(response.url)
			if check_url:
				check_url(self.clean_url)

			self._html = u""
			# # Extract from the <head> tag
			head = self._get_tag(response, tag_name="head")
			# print "Get head: %s" % len(head)
			extractor = extraction.SvvenExtractor(techniques=[
				"extraction.techniques.FacebookOpengraphTags",
				"extraction.techniques.TwitterSummaryCardTags",
				"extraction.techniques.HeadTags"
			])
			extracted = extractor.extract(head, source_url=self.clean_url)
			self._load(**extracted)

			# # Extract from <body>
			if GET_ALL_DATA or not self._is_complete():
				body = self._get_tag(response, tag_name="body")
				# print "Get body: %s" % len(body)
				extractor = extraction.SvvenExtractor(techniques=[
					"extraction.techniques.HTML5SemanticTags",
					"extraction.techniques.SemanticTags"				
				])
				extracted = extractor.extract(body, source_url=self.clean_url)
				self._load(**extracted)
			del self._html # no longer needed

		# that's it

