# -*- coding: utf-8 -*-

from summary import Summary
from summary import config

def test_canonical_site_urls():
    config.NONCANONIC_SITES = ["c2.com", "www.ecommercebytes.com", "www.lukew.com", "cyberdust.com", 'forums.station.sony.com']
    config.USEFUL_QUERY_KEYS = ["page", "a", "h", "z"]
    s = Summary()

    # a sort query arguments, first by key, then by value
    # b percent encode paths and query arguments. non-ASCII characters are
    # c percent-encoded using UTF-8 (RFC-3986)
    # d normalize all spaces (in query arguments) '+' (plus symbol)
    # e normalize percent encodings case (%2f -> %2F)
    # f remove query arguments with blank values (unless site in NONCANONIC_SITES)
    # g remove fragments (unless #!)
    # h remove username/password at front of domain
    # i remove port if 80, keep if not
    # j change domain to lowercase
    # k remove query arguments (unless site in USEFUL_QUERY_KEYS)


    url = 'http://www.gmo-toku.jp/item/70228568/【YONEX】+パワークッションSC4メン+（SHB-SC4M+）'
    clean_url = s._clean_url(url)
    assert clean_url == 'http://www.gmo-toku.jp/item/70228568/%E3%80%90YONEX%E3%80%91+%E3%83%91%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3SC4%E3%83%A1%E3%83%B3+%EF%BC%88SHB-SC4M+%EF%BC%89'

    url = "http://www.mavs.com/videos/run-dmc-cant-be-stopped/"
    clean_url = s._clean_url(url)
    assert clean_url == "http://www.mavs.com/videos/run-dmc-cant-be-stopped"

    # 1 - h g i
    url = 'https://bob:bobby@www.lunatech.com:8080/file.jpg;p=1?a=3422#!page1/98292'
    clean_url = s._clean_url(url)
    assert clean_url == "https://www.lunatech.com:8080/file.jpg;p=1?a=3422#!page1/98292"

    # 2 - h g i
    url = 'https://bob:bobby@www.lunatech.com:8080/file.jpg;p=1?q=2#third'
    clean_url = s._clean_url(url)
    assert clean_url == "https://www.lunatech.com:8080/file.jpg;p=1"

    # 3 - i a b
    url = 'http://google.com:80/cgi?z=!@£$%^*()-+&a=!@£$%^ *()-+'
    clean_url = s._clean_url(url)
    assert clean_url == "http://google.com/cgi?a=%21%40%C2%A3%24%25%5E+%2A%28%29-+&z=%21%40%C2%A3%24%25%5E%2A%28%29-+"

    # 4 - i a
    url = "http://google.com:80/cgi?z=1&h=8&a=1"
    clean_url = s._clean_url(url)
    assert clean_url == "http://google.com/cgi?a=1&h=8&z=1"

    # 5 - j f
    url = "http://CYBERDUST.com:80/addme?urbandrones&page1"
    clean_url = s._clean_url(url)
    assert clean_url == 'http://cyberdust.com/addme?page1&urbandrones'

    # 6 - a f
    url = "http://www.lukew.com/ff/entry.asp?1696&893489&3333"
    clean_url = s._clean_url(url)
    assert clean_url == 'http://www.lukew.com/ff/entry.asp?1696&3333&893489'

    # 7 - f j
    url = "http://www.ecommercebytes.COM/C/blog/blog.pl?/pl/2014/12/1417625708.htm"
    clean_url = s._clean_url(url)
    assert clean_url == 'http://www.ecommercebytes.com/C/blog/blog.pl?%2Fpl%2F2014%2F12%2F1417625708.htm'

    # 8 - f
    url = "https://forums.station.sony.com/ps2/index.php?threads/welcome-to-the-planetside-2-closed-beta.212516/"
    clean_url = s._clean_url(url)
    assert clean_url == 'https://forums.station.sony.com/ps2/index.php?threads%2Fwelcome-to-the-planetside-2-closed-beta.212516%2F'

    # 9 - a f
    url = "http://c2.com/cgi/wiki?LispMacro&p=1&BParam#DROPME"
    clean_url = s._clean_url(url)
    assert clean_url == "http://c2.com/cgi/wiki?BParam&LispMacro&p=1"

    # 11 - a f
    url = "http://c2.com/cgi/wiki?LispMacro&p=1&BParam&zzz#!KEEPME"
    clean_url = s._clean_url(url)
    assert clean_url == "http://c2.com/cgi/wiki?BParam&LispMacro&p=1&zzz#!KEEPME"

    # 12 - f j k
    url = "http://I_AM_NORMAL_URL.com/cgi?xxx&yyy=1"
    clean_url = s._clean_url(url)
    assert clean_url == "http://i_am_normal_url.com/cgi"

    # 13 - i k
    url = "http://google.com:80/cgi?xxx&page=1"
    clean_url = s._clean_url(url)
    assert clean_url == "http://google.com/cgi?page=1"

    # 14
    url = "http://www.google.com/cgi?page=1 and 3"
    clean_url = s._clean_url(url)
    assert clean_url == "http://www.google.com/cgi?page=1+and+3"
