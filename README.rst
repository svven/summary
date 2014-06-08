=======
Summary
=======

Simple usage
------------

Working with the ``summary`` package::

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

If you fork or clone the repo you can use summarize.py like this::

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
    -> http://www.nytimes.com/
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/33/ad.373366/bar1-3panel-nyt.png
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/33/ad.373366/bar1-3panel-nytcom.png
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/33/ad.373366/bar1-4panel-opinion.png
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/51/ad.375173/CRS-1572_nytpinion_EARS_L_184x90_CP2.gif
    [BadImage] AdblockURLFilter: http://graphics8.nytimes.com/adx/images/ADS/37/51/ad.375174/CRS-1572_nytpinion_EARS_R_184x90_ER1.gif
    [BadImage] RatioImageException(379, 64): http://i1.nyt.com/images/misc/nytlogo379x64.gif
    [BadImage] TinyImageException(16, 16): http://graphics8.nytimes.com/images/article/functions/facebook.gif
    [BadImage] TinyImageException(16, 16): http://graphics8.nytimes.com/images/article/functions/twitter.gif-> http://www.technologyreview.com/lists/technologies/2014/
    Success: 3.
    >>> html = render(template="news.html",
        summaries=summaries, result=result, speed=speed)
    >>> with open('demo.html', 'w') as file:
    ...   file.write(html)
    >>> 

In a nutshell
-------------

Summary requests the page from the URL, then uses
`extraction <https://github.com/lethain/extraction>`__ to parse the
HTML. 

Worth mentioning that it downloads the head tag first, performs
specific extraction techniques, and goes further to body only if
extracted data is not complete. Unless ``summary.GET_ALL_DATA = True``.

The resulting lists of titles, images, and descriptions are filtered on
the fly to rule out unwanted items like ads, tiny images (tracking
images or sharing buttons), and plain white images. See the whole list
of filters below.

Many thanks to Will Larson (`@lethain <https://github.com/lethain>`__)
for adapting his `extraction <https://github.com/lethain/extraction>`__
library to version 0.2 to accomodate summary.

Rendering
---------

The purpose of the HTML rendering mechanism is just to visualize
extracted data. 
The included Jinja2 template (news.html) is built on top of bootstrap and displays the summaries in a nice responsive grid layout.

You can completely disregard the rendering mechanism and just
import summary module for data extraction and filtering. You probably
have your own means to render the data, so you only need the summary
folder.

|image|

![news.html
preview](\ https://dl.dropboxusercontent.com/u/134594/Svven/news.png)

This is the output having ``summary.GET_ALL_DATA = True``.

**Clicking the summary title, image and description cycles through the
multiple extracted values.**

<https://dl.dropboxusercontent.com/u/134594/svven/news.html>



And this one produced much faster (see footer) with
``summary.GET_ALL_DATA = False``. It contains only the first valid item
of each kind - title, image, and description. This is the default
behaviour. 

<https://dl.dropboxusercontent.com/u/134594/svven/fast.html>

Installation
------------
Pip it for simple usage::

    $ pip install summary-extraction


Or clone the repo if you need rendering::

    $ virtualenv env 
    $ source env/bin/activate
    $ git clone https://github.com/svven/summary.git 
    $ pip install -r summary/requirements.txt 

    $ cd summary # path to templates is relative 
    $ python # see the usage instructions above

Requirements
------------
Base required packages are ``extraction`` and ``requests``, but it doesn't do much withouth ``adblockparser`` and ``Pillow``::

    Jinja2==2.7.2 # only for rendering 
    Pillow==2.4.0
    adblockparser==0.2
    extraction==0.2 
    lxml==3.3.5 
    re2==0.2.20 # good for adblockparser
    requests==2.2.1

Filters
-------

Filters are *callable* classes that perform specific data checks.

For the moment there are only image filters. The image URL is passed as
input parameter to the first filter. The check is performed and the URL
is returned if it is valid, so it is passed to the second filter and so
on. When the check fails it returns ``None``.

This pattern makes it possible to write the filtering routine like this::

    def _filter_image(self, url):
      "The param is the image URL, which is returned if it passes *all* the filters."
      return reduce(lambda f, g: f and g(f), 
        [
          filters.AdblockURLFilter()(url),
          filters.NoImageFilter(),
          filters.SizeImageFilter(),
          filters.MonoImageFilter(),
          filters.FormatImageFilter(),
        ])

    images = filter(None, map(self._filter_image, image_urls))

- **AdblockURLFilter**

   Uses `adblockparser <https://github.com/scrapinghub/adblockparser>`__
   and returns ``None`` if it ``should_block`` the URL. 
   
   Hats off to Mikhail Korobov (`@kmike <https://github.com/kmike>`__) for the
   awesome work. It gives a lot of value to this mashup repo.

- **NoImageFilter**

   Retrieves actual image file, and returns ``None`` if it fails. 
   
   Otherwise it returns an instance of the ``filters.Image`` class
   containing the URL, together with the size and format of the actual
   image. Basically it hydrates this instance which is passed to
   following filters. 
   The ``Image.__repr__`` override returns just
   the URL so we can write the beautiful filtering routine you can see
   above.

   Worth mentioning again that it only gets first few chunks of the
   image file until the PIL parser gets the size and format of the
   image.

- **SizeImageFilter**

   Checks the ``filters.Image`` instance to have proper size. 
   
   This can raise following exceptions based on defined limits:
   ``TinyImageException``, ``HugeImageException``, or
   ``RatioImageException``. If any of these happens it returns ``None``.

- **MonoImageFilter**

   Checks whether the image is plain white and returns ``None``. 
   
   This filter retrieves the whole image file so it has an extra regex
   check before. E.g.: rules out these URLs: 
   
   - http://wordpress.com/i/blank.jpg?m=1383295312g 
   - http://images.inc.com/leftnavmenu/inc-logo-white.png

- **FormatImageFilter**

   Rules out animated gif images for the moment. 
   This can be extended to exclude other image formats based on file contents.


That's it for now. You're very welcome to contribute. 

Comments and suggestions are welcome as well. Cheers, `@ducu <http://twitter.com/ducu>`__


.. |image| image:: https://dl.dropboxusercontent.com/u/134594/Svven/news.png
