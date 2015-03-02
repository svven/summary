from summary import Summary
from summary import config

def test_non_canonical_site_urls():
    config.NONCANONIC_SITES = ["c2.com"]
    config.USEFUL_QUERY_KEYS = []

    url = "http://c2.com/cgi/wiki?LispMacro&p=1"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert url == clean_url

    url = "http://c2.com/cgi/wiki?LispMacro&p=1&BParam"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert clean_url == "http://c2.com/cgi/wiki?BParam&LispMacro&p=1"

    url = "http://c2.com/cgi/wiki?LispMacro&p=1&BParam&zzz"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert clean_url == "http://c2.com/cgi/wiki?BParam&LispMacro&p=1&zzz"

    url = "http://I_AM_NORMAL_URL/cgi?xxx&yyy=1"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert clean_url == "http://i_am_normal_url/cgi"
