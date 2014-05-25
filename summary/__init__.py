"""
Summary class improves extraction.Extracted by providing
incremental load mechanism, and especially image validation.

But the main difference is that it performs the requests.

Extraction is performed gradually by parsing the HTML <head>
tag first, applying specific head extraction techniques, and
goes on to the <body> only if Summary data is not complete.
"""
import extraction, requests

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
		"Return the best url, if any."
		if self.urls:
			return self.urls[0]
		else:
			return None


	def _is_complete(self):
		# return False
		return self.title and self.description and self.image and self.url \
			and True

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


	def extract(self):
		"""
		Download the HTML <head> tag first, load it and see 
		if Summary data is complete. Otherwise download the HTML <body> 
		as well and load it by passing the appropriate techniques.
		"""
		extractor = extraction.Extractor(techniques=
			["extraction.techniques.FacebookOpengraphTags",
			 "extraction.techniques.HeadTags"])

		page = requests.get(self.source_url, timeout=10)
		page.raise_for_status()

		extracted = extractor.extract(page.text, source_url=page.url)

		self._load(**extracted)

