"""
Wrapper for `requests`.
"""

import requests
from config import USER_AGENT

def get(url, **kwargs):
	"""
	Wrapper for `request.get` function to set params.
	"""
	headers = kwargs.get('headers', {})
	headers['User-Agent'] = USER_AGENT # overwrite
	kwargs['headers'] = headers
	return requests.get(url, **kwargs)
