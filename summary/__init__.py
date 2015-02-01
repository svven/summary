"""
Summary class improves extraction.Extracted by providing
incremental load mechanism, and especially image validation.

But the main difference is that it performs the requests.

Extraction is performed gradually by parsing the HTML <head>
tag first, applying specific head extraction techniques, and
goes on to the <body> only if Summary data is not complete.
"""
from contextlib import closing
from urlparse import urlparse

import extraction
from w3lib.url import url_query_cleaner

import config
import request
import filters
from utils import convert
from url import canonicalize_url


site = lambda myurl: urlparse(myurl).netloc

class HTMLParseError(Exception):
    pass


class Summary(object):
    "Provides incremental load mechanism and validation."

    def __init__(self, source_url=None):
        """
        Unlike Extracted ctor, this one just sets the source_url.
        Extracted data is loaded later gradually by calling extract.
        """
        self.titles = []
        self.descriptions = []
        self.images = []
        self.urls = []
        self.source_url = source_url
        self.clean_url = self.source_url

        self._html = "" # Move here so it doesn't interfere with unit testing.
                        # Have to make sure it doesn't break normal operation.

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


    def _is_clear(self):
        return not (self.titles or self.descriptions or self.images or self.urls)

    def _is_complete(self):
        return self.titles and self.descriptions and self.images and self.urls and True

    def _clear(self):
        self.titles = []
        self.descriptions = []
        self.images = []
        self.urls = []

    def _load(self, titles=[], descriptions=[], images=[], urls=[], **kwargs):
        """
        Loads extracted data into Summary.
        Performs validation and filtering on-the-fly, and sets the
        non-plural fields to the best specific item so far.
        If GET_ALL_DATA is False, it gets only the first valid item.
        """
        enough = lambda items: items  # len(items) >= MAX_ITEMS

        if config.GET_ALL_DATA or not enough(self.titles):
            self.titles.extend(titles)

        if config.GET_ALL_DATA or not enough(self.descriptions):
            self.descriptions.extend(descriptions)

        if config.GET_ALL_DATA or not enough(self.urls):
            # urls = [self._clean_url(u) for u in urls]
            urls = map(self._clean_url, urls)
            self.urls.extend(urls)

        if config.GET_ALL_DATA:
            # images = [i for i in [self._filter_image(i) for i in images] if i]
            images = filter(None, map(self._filter_image, images))
            self.images.extend(images)
        elif not enough(self.images):
            for i in images:
                image = self._filter_image(i)
                if image:
                    self.images.append(image)
                if enough(self.images):
                    break

                    # Picking the best item by sorting
                    # self.titles = sorted(self.titles, key=len)
                    # self.descriptions = sorted(self.descriptions, key=len, reverse=True)
                    # self.images = sorted(self.images, key=lambda i: sum(i.size), reverse=True)

    def _clean_url(self, url):
        """
        Canonicalizes the url, as it is done in Scrapy.
        And keeps only USEFUL_QUERY_KEYS. It also strips the
        trailing slash to help identifying dupes.
        """
        clean_url = url_query_cleaner(url,
                                      parameterlist=config.USEFUL_QUERY_KEYS)  # , remove=True
        return canonicalize_url(clean_url).rstrip('/')

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
        """
        Iterates response content and returns the tag if found.
        If not found, the response content is fully consumed so
        self._html equals response.content, and it returns None.
        """
        lower_html = self._html.lower()
        tag_start = tag_end = None

        def find_tag(html, tag_name, tag_start, tag_end):
            if not tag_start:
                start = html.find("<%s" % tag_name)
                if start >= 0: tag_start = start
            if tag_start:
                end = html.find("</%s>" % tag_name)
                if end > tag_start: tag_end = end + len(tag_name) + 3
            if tag_end:  # and tag_start
                return self._html[tag_start:tag_end]
            return None

        consumed = hasattr(response, 'consumed') and \
                   getattr(response, 'consumed')
        if not consumed:
            for chunk in response.iter_content(config.CHUNK_SIZE):  # , decode_unicode=True
                self._html += chunk
                lower_html += chunk.lower()
                tag = find_tag(lower_html, tag_name, tag_start, tag_end)
                if tag:
                    return tag
                if len(self._html) > config.HTML_MAX_BYTESIZE:
                    raise HTMLParseError('Maximum response size reached.')
            response.consumed = True
        tag = find_tag(lower_html, tag_name, tag_start, tag_end)
        return tag


    def _extract(self, html, url, techniques):
        extractor = extraction.SvvenExtractor(techniques=techniques)
        extracted = extractor.extract(html, source_url=url)
        self._load(**extracted)


    def phantom_get(self, url):
        from selenium import webdriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = config.PHANTOMJS_USERAGENT
        driver = webdriver.PhantomJS(desired_capabilities=dcap, executable_path=config.PHANTOMJS_BIN)
        driver.set_window_size(1120, 550)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html


    def extract(self, check_url=None, http_equiv_refresh=True):
        """
        Downloads HTML <head> tag first, extracts data from it using
        specific head techniques, loads it and checks if is complete.
        Otherwise downloads the HTML <body> tag as well and loads data
        extracted by using appropriate semantic techniques.

        Eagerly calls check_url(url) if any, before parsing the HTML.
        Provided function should raise an exception to break extraction.
        E.g.: URL has been summarized before; URL points to off limits
        websites like foursquare.com, facebook.com, bitly.com and so on.
        """
        # assert self._is_clear()
        print "Requesting"
        with closing(request.get(self.clean_url, stream=True)) as response:
            response.raise_for_status()
            mime = response.headers.get('content-type')
            if mime and not ('html' in mime.lower()):
                raise HTMLParseError('Invalid Content-Type: %s' % mime)
            print "Cleaning"
            self.clean_url = self._clean_url(response.url)
            if check_url is not None:
                check_url(url=self.clean_url)
                print "Checked"

            encoding = config.ENCODING or response.encoding
            print "Extracting"

            if site(self.clean_url) in config.JS_WEBSITES:
                self._html = self.phantom_get(self.clean_url)
                response.consumed = True

            head = self._get_tag(response, tag_name="head")
            if http_equiv_refresh:
                # Check meta http-equiv refresh tag
                html = convert(head or self._html, encoding)
                self._extract(html, self.clean_url, [
                    "summary.techniques.HTTPEquivRefreshTags",
                ])
                new_url = self.urls and self.urls[0]
                if new_url and new_url != self.clean_url:
                    print "New url: %s" % new_url
                    self._clear()
                    self.clean_url = new_url
                    return self.extract(check_url=check_url, http_equiv_refresh=False)

            if head:
                print "Get head: %s" % len(head)
                self._extract(head, self.clean_url, [
                    "extraction.techniques.FacebookOpengraphTags",
                    "extraction.techniques.TwitterSummaryCardTags",
                    "extraction.techniques.HeadTags"
                ])
            # else:
            # print "No head: %s" % self.clean_url

            if config.GET_ALL_DATA or not self._is_complete():
                body = self._get_tag(response, tag_name="body")
                if body:
                    print "Get body: %s" % len(body)
                    self._extract(body, self.clean_url, [
                        "extraction.techniques.HTML5SemanticTags",
                        "extraction.techniques.SemanticTags"
                    ])
                    # else:
                    # print "No body: %s" % self.clean_url

            if not head and not body:
                raise HTMLParseError('No head nor body tags found.')

            del self._html  # no longer needed

            # that's it

