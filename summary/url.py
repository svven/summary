"""
Copyright (c) Scrapy developers.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Scrapy nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


This module has been copied from here:
https://github.com/scrapy/scrapy/blob/master/scrapy/utils/url.py

Hence the above copyright notice.
"""
import urllib
import urlparse
from urllib import quote

import config
from urltools import extract, construct, normalize, URL
from urlnorm import norm






# scrapy.utils.url was moved to w3lib.url and import * ensures this move doesn't break old code
from w3lib.url import *


def unicode_to_str(text, encoding=None, errors='strict'):
    """Return the str representation of text in the given encoding. Unlike
    .encode(encoding) this function can be applied directly to a str
    object without the risk of double-decoding problems (which can happen if
    you don't use the default 'ascii' encoding)

    This function has been copied from here:
    https://github.com/scrapy/scrapy/blob/master/scrapy/utils/python.py
    """

    if encoding is None:
        encoding = 'utf-8'
    if isinstance(text, unicode):
        return text.encode(encoding, errors)
    elif isinstance(text, str):
        return text
    else:
        raise TypeError('unicode_to_str must receive a unicode or str object, got %s' % type(text).__name__)


def url_is_from_any_domain(url, domains):
    """Return True if the url belongs to any of the given domains"""
    host = parse_url(url).netloc.lower()

    if host:
        return any(((host == d.lower()) or (host.endswith('.%s' % d.lower())) for d in domains))
    else:
        return False


def url_has_any_extension(url, extensions):
    return posixpath.splitext(parse_url(url).path)[1].lower() in extensions


def getFragment(url, keep_fragments):
    fragment = extract(norm(url)).fragment
    return fragment if fragment.startswith('!') or keep_fragments else ''


def canonicalize_url(url, keep_params=False, keep_fragments=False):
    """Canonicalize the given url by applying the following procedures:

    # a sort query arguments, first by key, then by value
    # b percent encode paths and query arguments. non-ASCII characters are
    # c percent-encoded using UTF-8 (RFC-3986)
    # d normalize all spaces (in query arguments) '+' (plus symbol)
    # e normalize percent encodings case (%2f -> %2F)
    # f remove query arguments with blank values (unless site in NONCANONIC_SITES)
    # g remove fragments (unless #!)
    # h remove username/password at front of domain
    # i remove port if 80, keep if not
    # k remove query arguments (unless site in USEFUL_QUERY_KEYS)

    The url passed can be a str or unicode, while the url returned is always a
    str.
    """
    if keep_params:
        # Preserve all query params
        parsed = extract(norm(url))
    else:
        # Remove unwanted params
        parsed = extract(url_query_cleaner(normalize(url), parameterlist=config.USEFUL_QUERY_KEYS))

    # Sort params, remove blank if not wanted
    query = urllib.urlencode(sorted(urlparse.parse_qsl(parsed.query, keep_blank_values=keep_params)))
    fragment = getFragment(url, keep_fragments)

    # The following is to remove orphaned '=' from query string params with no values
    query = re.sub(r"=$", "", query.replace("=&", "&"))

    # Reconstruct URL, escaping apart from safe chars
    # See http://stackoverflow.com/questions/2849756/list-of-valid-characters-for-the-fragment-identifier-in-an-url
    # http://stackoverflow.com/questions/4669692/valid-characters-for-directory-part-of-a-url-for-short-links
    safe = "/.-_~!$&'()*+,;=:@"
    newurl = construct(URL(parsed.scheme, '', '', parsed.subdomain, parsed.domain, parsed.tld, parsed.port, quote(parsed.path, safe=safe), query, quote(fragment, safe=safe), ''))
    return newurl.rstrip('/')




def _unquotepath(path):
    for reserved in ('2f', '2F', '3f', '3F'):
        path = path.replace('%' + reserved, '%25' + reserved.upper())
    return urllib.unquote(path)


def parse_url(url, encoding=None):
    """Return urlparsed url from the given argument (which could be an already
    parsed url)
    """
    return url if isinstance(url, urlparse.ParseResult) else \
        urlparse.urlparse(unicode_to_str(url, encoding))

