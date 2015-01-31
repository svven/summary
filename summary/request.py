"""
Wrapper for `requests`.
"""
import logging

import requests

logger = logging.getLogger(__name__)

from config import USER_AGENT, TIMEOUT

requests.packages.urllib3.disable_warnings()

def get(url, **kwargs):
	"""
	Wrapper for `request.get` function to set params.
	"""
	headers = kwargs.get('headers', {})
	headers['User-Agent'] = USER_AGENT # overwrite
	kwargs['headers'] = headers

	timeout = kwargs.get('timeout', TIMEOUT)
	kwargs['timeout'] = timeout

	kwargs['verify'] = False # no SSLError

	logger.debug("Getting: %s", url)
	return requests.get(url, **kwargs)
