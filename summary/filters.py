"This file contains filters for the extracted data, mainly images."

from __future__ import division
import requests
from contextlib import closing

clsn = lambda e: e.__class__.__name__

class Image(object):
	"Used by the filter classes in this module."
	def __init__(self, url, size=None, format=None): # raw_image=None
		self.url = url
		self.size = size
		self.format = format
		# self.raw = raw_image # for MonoImageFilter
	
	def __repr__(self):
		return self.url # this is important


from adblockparser import AdblockRules

ADBLOCK_RULES = [
	'||ad.doubleclick.net', 
	'.gravatar.com/avatar/', '.media.tumblr.com/avatar_', 'assets.tumblr.com/images/default_avatar/',
]
ADBLOCK_EASYLIST = 'https://easylist-downloads.adblockplus.org/easylist.txt'

class AdblockURLFilter(object): # Filter
	"Uses Adblock URL filtering and returns None if should_block."
	
	def get_rules():
		"Loads Adblock filter rules from file."
		raw_rules = []
		raw_rules.extend(ADBLOCK_RULES)
		with closing(requests.get(ADBLOCK_EASYLIST, stream=True)) as file:
			# lines = 0 # to be removed
			for rule in file.iter_lines():
				raw_rules.append(rule.strip())
				# lines += 1 # tbr
				# if lines == 2500: break # tbr, only for windoze with no re2
		rules = AdblockRules(raw_rules)
		return rules

	rules = get_rules() # static

	def __call__(self, url):
		if AdblockURLFilter.rules.should_block(url):
			print "[BadImage] AdblockURLFilter: %s" % url
			return None
		return url


from PIL.Image import Image as PILImage
from PIL.ImageFile import Parser as PILParser

CHUNK_SIZE = 1024 # 1 KB
IMAGE_MAX_BYTESIZE = 1 * 1048576 # 1 MB

class NoImageFilter(object): # AdblockURLFilter
	"""
	Retrieves actual image and returns it, or None if it fails.
	Returns instance of Image class to be verified by following filters.
	"""
	class MaxBytesException(Exception):
		pass
	
	class ZeroBytesException(Exception):
		pass

	class NoImageException(Exception):
		pass
	
	@classmethod
	def get_image(cls, url):
		"""
		Returned Image instance has response url.
		This might be different than the url param because of redirects.
		"""
		length = 0
		raw_image = None
		with closing(requests.get(url, stream=True)) as response:
			response.raise_for_status()
			response_url = response.url
			parser = PILParser()
			for chunk in response.iter_content(CHUNK_SIZE):
				length += len(chunk)
				if length > IMAGE_MAX_BYTESIZE:
					del parser
					raise cls.MaxBytesException
				parser.feed(chunk)
				# comment this to get the whole file
				if parser.image and parser.image.size:
					raw_image = parser.image
					del parser # free some memory
					break
			# or this to get just the size and format
			# raw_image = parser.close()
		if length == 0:
			raise cls.ZeroBytesException
		if not raw_image:
			raise cls.NoImageException
		image = Image(response_url, raw_image.size, raw_image.format)
		return image

	def __call__(self, url):
		# url = super(NoImageFilter, self).__call__(url)
		try:
			image = NoImageFilter.get_image(url)
			return image
		except Exception, e:
			print "[BadImage] %s: %s" % (clsn(e), url)
			pass
		return None


IMAGE_LIMIT_RATIO = 4 # if js crop center square
IMAGE_MIN_IMGSIZE = (64, 64)
IMAGE_MAX_IMGSIZE = (2064, 2064)

class SizeImageFilter(object): # NoImageFilter
	"""
	Checks image to have proper size, or returns None if it doesn't.
	This may rule out tracking images that were not detected by AdblockURLFilter.
	"""
	class TinyImageException(Exception):
		pass
	
	class HugeImageException(Exception):
		pass

	class RatioImageException(Exception):
		pass
	
	@classmethod
	def check_size(cls, image):
		if  image.size[0] < IMAGE_MIN_IMGSIZE[0] or \
			image.size[1] < IMAGE_MIN_IMGSIZE[1]:
			raise cls.TinyImageException
		if  image.size[0] > IMAGE_MAX_IMGSIZE[0] or \
			image.size[1] > IMAGE_MAX_IMGSIZE[1]:
			raise cls.HugeImageException
		ratio = image.size[0] / image.size[1]
		if ratio < 1:
			ratio = 1 / ratio
		if  ratio > IMAGE_LIMIT_RATIO:
			raise cls.RatioImageException

	def __call__(self, image):
		# image = super(SizeImageFilter, self).__call__(image)
		try:
			SizeImageFilter.check_size(image)
			return image
		except Exception, e:
			print "[BadImage] %s%s: %s" % (clsn(e), image.size, image.url)
			pass
		return None


import re, PIL
from cStringIO import StringIO

IMAGE_MONO_REGEX = re.compile(r'((_|\b)(white|blank|black|overlay)(_|\b))', re.IGNORECASE) # improve this

class MonoImageFilter(object): # SizeImageFilter
	"""
	Checks whether the image is (plain black or) white and returns None.
	Otherwise return the Image instance.
	
	E.g.:
		http://upcoming.org/assets/images/screw-it.png#SEMT
		http://i.cdn.turner.com/cnn/.e/img/3.0/global/header/intl/CNNi_Logo_new.png#SEMT
		http://images.inc.com/leftnavmenu/inc-logo-white.png#SEMT
		http://www.inc.com/uploaded_files/leftnavmenuitem/UNUM_38.png#SEMT
		http://wordpress.com/i/blank.jpg?m=1383295312g#FBOG
		http://www.niemanlab.org/wordpress/wp-content/themes/Labby/resources/iphone-menu-fire-white-small.png#SEMT
		https://d8o6wu1tc2zf3.cloudfront.net/pegasus/4.5.113/bundles/lockerzglobal/images/decal_back_overlay.png?1.0.0#SEMT
	"""
	class MonoImageException(Exception):
		pass
	
	@classmethod
	def check_color(cls, raw_image):
		"""
		Just check if raw_image is completely white.
		http://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
		"""
		# sum(img.convert("L").getextrema()) in (0, 2)
		extrema = raw_image.convert("L").getextrema()
		if extrema == (255, 255): # all white
			raise cls.MonoImageException

	def __call__(self, image):
		# image = super(MonoImageFilter, self).__call__(image)
		try:
			if IMAGE_MONO_REGEX.search(image.url):
				content = requests.get(image.url).content
				pic = StringIO(content)
				raw_image = PIL.Image.open(pic)
				MonoImageFilter.check_color(raw_image)
				del raw_image # more cleaning maybe
				print "[GoodImage] MonoImageFilter: %s" % image.url
			return image
		except Exception, e:
			print "[BadImage] %s: %s" % (clsn(e), image.url)
			pass
		return None


class FormatImageFilter(object): # MonoImageFilter
	"""
	Checks whether the image is animated gif.
	"""
	class AnimatedImageException(Exception):
		pass

	@classmethod
	def check_animated(cls, raw_image):
		"Checks whether the gif is animated."
		try:
			raw_image.seek(1)
		except EOFError:
			isanimated= False
		else:
			isanimated= True
			raise cls.AnimatedImageException


	def __call__(self, image):
		# image = super(FormatImageFilter, self).__call__(image)
		try:
			if image.format.lower() == "gif":
				content = requests.get(image.url).content
				pic = StringIO(content)
				raw_image = PIL.Image.open(pic)
				FormatImageFilter.check_animated(raw_image)
				del raw_image
				print "[GoodImage] FormatImageFilter: %s" % image.url
			return image
		except Exception, e:
			print "[BadImage] %s: %s" % (clsn(e), image.url)
			pass
		return None


