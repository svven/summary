Summary
=======

Simple usage
------------

    >>> import summary
    >>> s = summary.Summary('https://github.com/svven/summary')
    >>> s.extract()
    >>> s.title
    u'svven/summary'
    >>> s.image
    https://avatars0.githubusercontent.com/u/7524085?s=400
    >>> s.description
    u'summary - Summary is a complete solution to extract the title, image and description from any URL.'
    
Batch usage with HTML rendering
-------------------------------
    
    >>> import summary
    >>> summary.GET_ALL_DATA = True # default is False
    >>> urls = [
            'http://www.wired.com/',
            'http://www.nytimes.com/', 
            'http://www.technologyreview.com/lists/technologies/2014/'
        ]
    >>> from summarize import summarize, render
    >>> summaries, result, speed = summarize(urls)
    -> http://www.wired.com/
    [BadImage] RatioImageException(398, 82): http://www.wired.com/wp-content/vendor/condenast/pangea/themes/wired/assets/images/wired_logo.gif
    [BadImage] TinyImageException(150, 60): http://www.wired.com/wp-content/vendor/condenast/pangea/themes/wired/assets/images/post_wired_logo_150x60.gif
    -> http://www.nytimes.com/
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/24/ad.372455/bar1_memorialday.jpg
    [BadImage] AdblockURLFilter: http://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=bsr&FlightID=9912966&Page=&PluID=0&Pos=1206468759
    [BadImage] RatioImageException(379, 64): http://i1.nyt.com/images/misc/nytlogo379x64.gif
    [BadImage] TinyImageException(16, 16): http://graphics8.nytimes.com/images/article/functions/facebook.gif
    [BadImage] TinyImageException(16, 16): http://graphics8.nytimes.com/images/article/functions/twitter.gif
    -> http://www.technologyreview.com/lists/technologies/2014/
    Success: 3.
    >>> html = render(template="news.html",
        summaries=summaries, result=result, speed=speed)
    >>> with open('demo.html', 'w') as file:
    ...   file.write(html)
    >>> 


Summary requests the page from the URL, then uses 
[extraction](https://github.com/svven/extraction) to parse the HTML.<br />
Worth mentioning that it downloads the <head> tag first, performs specific
extraction techniques, and goes further to <body> only if extracted data is 
not complete. (Unless you set ```summary.GET_ALL_DATA``` to True.)

The resulting lists of titles, images, and descriptions are then filtered 
to rule out unwanted items like ads, tiny images (tracking images or sharing 
buttons), and plain white images. See the whole list of filters below.

Many thanks to Will Larson ([@lethain](https://github.com/lethain)) 
for the original [extraction](https://github.com/lethain/extraction) repo.<br />
Here's the forked extraction package that's being used: 
https://github.com/svven/extraction


Notes
=============

The purpose of the HTML rendering mechanism is just to visualize extracted data. 
The included template (news.html) is built on top of bootstrap and displays the 
summaries in a nice responsive grid layout.

**Clicking the summary title, image and description cycles through the multiple 
extracted values.**

![news.html preview](https://dl.dropboxusercontent.com/u/134594/Svven/news.png)
https://dl.dropboxusercontent.com/u/134594/svven/news.html

Installation
============

Cloning both summary and extraction repos.

    $ virtualenv env
    $ source env/bin/activate # or env\scripts\activate
    $ git clone https://github.com/svven/extraction.git
    $ git clone https://github.com/svven/summary.git
    $ pip install -r summary/requirements.txt # includes extraction dependencies but the extraction itself
    $ pip install -e extraction/ # instead of `python setup.py develop`
    
    $ cd summary # path to templates is relative
    $ python # see the Usage section above

Requirements
============

    Jinja2==2.7.2 # only for rendering
    MarkupSafe==0.23 # idem
    Pillow==2.4.0
    adblockparser==0.2 # very useful
    beautifulsoup4==4.3.2
    # extraction==0.1.3 # pip install -e .
    html5lib==0.999
    lxml==3.3.5
    re2==0.2.20 # install re2 first
    requests==2.2.1
    six==1.6.1
    wsgiref==0.1.2



***
You're very welcome to contribute. <br />
Comments and suggestions are welcome as well. Cheers,
[@ducu](http://twitter.com/ducu)

