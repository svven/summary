"This file contains additional extraction techniques."
from bs4 import BeautifulSoup
from extraction.techniques import Technique


class HTTPEquivRefreshTags(Technique):
	"""
	Extract http-equiv refresh url to follow.

		<meta http-equiv="refresh" 
			content="0;url=http://www.quora.com/Startup-Ideas/What-are-the-best-ways-to-think-of-ideas-for-a-startup">

	"""
	key_attr = 'http-equiv'
	val_attr = 'refresh' #

	def clean_refresh_url(self, url):
		# e.g. Firefox 1.5 does (something like) this
		if ((url.startswith('"') and url.endswith('"')) or
			(url.startswith("'") and url.endswith("'"))):
			url = url[1:-1]
		return url

	def parse_refresh_header(self, refresh):
		"""
		>>> parse_refresh_header("1; url=http://example.com/")
		(1.0, 'http://example.com/')
		>>> parse_refresh_header("1; url='http://example.com/'")
		(1.0, 'http://example.com/')
		>>> parse_refresh_header("1")
		(1.0, None)
		>>> parse_refresh_header("blah")  # doctest: +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		ValueError: invalid literal for float(): blah
		"""
		ii = refresh.find(";")
		if ii != -1:
			pause, newurl_spec = float(refresh[:ii]), refresh[ii+1:]
			jj = newurl_spec.find("=")
			key = None
			if jj != -1:
				key, newurl = newurl_spec[:jj], newurl_spec[jj+1:]
				newurl = self.clean_refresh_url(newurl)
			if key is None or key.strip().lower() != "url":
				raise ValueError()
		else:
			pause, newurl = float(refresh), None
		return pause, newurl

	def extract(self, html):
		"Extract http-equiv refresh url to follow."
		extracted = {}
		soup = BeautifulSoup(html)
		for meta_tag in soup.find_all('meta'):
			if self.key_attr in meta_tag.attrs and 'content' in meta_tag.attrs and \
				meta_tag[self.key_attr].lower() == self.val_attr:
				refresh = meta_tag.attrs['content']
				try:
					pause, newurl = self.parse_refresh_header(refresh)
					if newurl:
						extracted['urls'] = [newurl]
						break # one is enough
				except:
					pass # nevermind
		return extracted
