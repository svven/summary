Summary
=======

### Simple usage

```python
>>> import summary
>>> s = summary.Summary('https://github.com/svven/summary')
>>> s.extract()
>>> s.title
u'svven/summary'
>>> s.image
https://avatars0.githubusercontent.com/u/7524085?s=400
>>> s.description
u'summary - Summary is a complete solution to extract the title, image and description from any URL.'
```

### Batch usage with HTML rendering

```python    
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
```

In a nutshell
-------------

Summary requests the page from the URL, then uses 
[extraction](https://github.com/svven/extraction) to parse the HTML.<br />
Worth mentioning that it downloads the head tag first, performs specific
extraction techniques, and goes further to body only if extracted data is 
not complete. Unless ```summary.GET_ALL_DATA = True```.

The resulting lists of titles, images, and descriptions are filtered on the fly 
to rule out unwanted items like ads, tiny images (tracking images or sharing 
buttons), and plain white images. See the whole list of filters below.

Many thanks to Will Larson ([@lethain](https://github.com/lethain)) 
for the original [extraction](https://github.com/lethain/extraction) repo.<br />
Here's the forked extraction package that's being used: 
https://github.com/svven/extraction


Notes
-----

The purpose of the HTML rendering mechanism is just to visualize extracted data.<br /> 
The included Jinja2 template (news.html) is built on top of bootstrap and displays the 
summaries in a nice responsive grid layout. 

You can completely disregard the rendering mechanism and just `import summary` module
for data extraction and filtering. You probably have your own means to render the data,
so you only need the summary folder.


![news.html preview](https://dl.dropboxusercontent.com/u/134594/Svven/news.png)

**Clicking the summary title, image and description cycles through the multiple 
extracted values.**

https://dl.dropboxusercontent.com/u/134594/svven/news.html


Installation
------------

Cloning both summary and extraction repos.

    $ virtualenv env
    $ source env/bin/activate # or env\scripts\activate
    $ git clone https://github.com/svven/extraction.git
    $ git clone https://github.com/svven/summary.git
    $ pip install -r summary/requirements.txt # includes extraction dependencies but the extraction itself
    $ pip install -e extraction/ # instead of `python setup.py develop`
    
    $ cd summary # path to templates is relative
    $ python # see the usage instructions above

Requirements
------------

    Jinja2==2.7.2 # only for rendering
    MarkupSafe==0.23 # idem
    Pillow==2.4.0
    adblockparser==0.2
    beautifulsoup4==4.3.2
    # extraction==0.1.3 # pip install -e .
    html5lib==0.999
    lxml==3.3.5
    re2==0.2.20 # install re2 first
    requests==2.2.1
    six==1.6.1
    wsgiref==0.1.2

Filters
-------

Filters are _callable_ classes that perform specific data checks.

For the moment there are only image filters. The image URL is passed as
input parameter to the first filter. The check is performed and the URL
is returned if it is valid, so it is passed to the second filter and so
on. When the check fails it returns `None`.

This pattern makes it possible to write the filtering routine like this

```python
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
```

* **AdblockURLFilter**

  Uses [adblockparser](https://github.com/scrapinghub/adblockparser) 
  and returns `None` if it `should_block` the URL.<br />
  Hats off to Mikhail Korobov ([@kmike](https://github.com/kmike)) for the awesome work.
  It gives a lot of value to this mashup repo.

* **NoImageFilter**

  Retrieves actual image file, and returns `None` if it fails.<br />
  Otherwise it returns an instance of the `filters.Image` class containing 
  the URL, together with the size and format of the actual image. Basically
  it hydrates this instance which is passed to following filters.<br />
  The `Image.__repr__` override returns just the URL so we can write the 
  beautiful filtering routine you can see above.
  
  Worth mentioning again that it only gets first few chunks of the image
  file until the `PIL` Parser gets the size and format of the image.

* **SizeImageFilter**

  Checks the `filters.Image` instance to have proper size.<br />
  This can raise following exceptions based on defined limits: `TinyImageException`, 
  `HugeImageException`, or `RatioImageException`. 
  If any of these happens it returns `None`.

* **MonoImageFilter**

  Checks whether the image is plain white and returns None.<br />
  This filter retrieves the whole image file so it has an extra
  regex check before. It rules out following URLs:
    - http://wordpress.com/i/blank.jpg?m=1383295312g
    - http://images.inc.com/leftnavmenu/inc-logo-white.png

* **FormatImageFilter**

  Rules out animated gif images for the moment.<br />
  This can be extended to exclude other image formats based on file contents.


***
You're very welcome to contribute. <br />
Comments and suggestions are welcome as well. Cheers,
[@ducu](http://twitter.com/ducu)

