from summary import Summary
from summary import config

def test_non_canonical_site_urls():
    config.NONCANONIC_SITES = ["c2.com", "www.ecommercebytes.com", "www.lukew.com", "cyberdust.com", 'forums.station.sony.com']
    config.USEFUL_QUERY_KEYS = []

    url = "http://cyberdust.com/addme?urbandrones"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert url == clean_url

    url = "http://www.lukew.com/ff/entry.asp?1696"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert url == clean_url

    url = "http://www.ecommercebytes.com/C/blog/blog.pl?/pl/2014/12/1417625708.htm"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert clean_url == 'http://www.ecommercebytes.com/C/blog/blog.pl?%2Fpl%2F2014%2F12%2F1417625708.htm'

    url = "https://forums.station.sony.com/ps2/index.php?threads/welcome-to-the-planetside-2-closed-beta.212516/"
    s = Summary(url)
    clean_url = s._clean_url(url)
    assert clean_url == 'https://forums.station.sony.com/ps2/index.php?threads%2Fwelcome-to-the-planetside-2-closed-beta.212516%2F'

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
