Summary
=======

Uses extraction to get the title, image and description 
for a bunch of URLs. <br />
Here's the forked extraction package that's being used: 
https://github.com/svven/extraction

Many thanks to Will Larson ([@lethain](https://github.com/lethain)) for the original repo:
https://github.com/lethain/extraction. <br />
Very nice work there, easy to extend -- summary is just a
wrapper over extraction, used to help extend and hopefully 
improve extraction.

Functionality
=============

Parses the provided list of urls, performs data extraction,
and renders the output in html format as news articles.
The included template is built on top of bootstrap and
displays the articles in a nice responsive grid layout.

**Clicking the article title, image and description cycles
through the multiple extracted values. This helps
visualizing extraction results.**

Docstrings
==========

```
extract(urls)
```
Parses each url and performs the extraction.
Returns a list of Extracted instances aka articles.

For now it downloads the whole page from the url in order
to perform the extraction. It would be better to define 
some extraction techniques that can work with fragments of
the HTML page so we could stream the request for faster 
processing and minimum bandwidth. Will keep this in mind.

```
render(articles, template)
```
Renders the html containing provided articles.

The article has to be an instance of extraction.Extracted, 
or at least contain similar properties: title, image, url,
description and lists/tuples titles, images, descriptions.

Feeds are not rendered at the moment - might be discarded.
(That's the best added value of this nice little library.)

```
summarize(urls, template='news.html')
```
Main function of the module.
Parses the list of urls, performs data extraction,
and renders the output in html format as news articles,
if not otherwise specified by the template.

***
You're very welcome to contribute. <br />
Comments and suggestions are welcome as well. Cheers,
[@ducu](http://twitter.com/ducu)

