"""
Wrapper for `requests`.
"""
import logging
logger = logging.getLogger("summary")

import requests
requests.packages.urllib3.disable_warnings()
import requests_html

from summary import config

def get(url, **kwargs):
    """
    Wrapper for `request.get` function to set params.
    """
    headers = kwargs.get('headers', {})
    headers['User-Agent'] = config.USER_AGENT # overwrite
    kwargs['headers'] = headers

    timeout = kwargs.get('timeout', config.TIMEOUT)
    kwargs['timeout'] = timeout

    kwargs['verify'] = False # no SSLError

    logger.debug("Getting: %s", url)
    return requests.get(url, **kwargs)

