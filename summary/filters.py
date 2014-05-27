"This file contains filters for the extracted data, mainly images."

import requests
from contextlib import closing

clsn = lambda e: e.__class__.__name__

class Image(object):
	"Used by the filter classes below."
	def __init__(self, url, size=None, format=None): # raw_image=None
		self.url = url
		self.size = size
		self.format = format
		# self.raw = raw_image # for MonoImageFilter
	
	def __repr__(self):
		return self.url # this is important


from adblockparser import AdblockRules

ADBLOCK_RULES = [
	'||ad.doubleclick.net', '.gravatar.com/avatar/', '.media.tumblr.com/avatar_',
]
ADBLOCK_EASYLIST = 'https://easylist-downloads.adblockplus.org/easylist.txt'

class AdblockURLFilter(object): # Filter
	"Uses Adblock URL filtering and returns None if should_block."
	
	def get_rules():
		"Loads Adblock filter rules from file."
		raw_rules = []
		raw_rules.extend(ADBLOCK_RULES)
		with closing(requests.get(ADBLOCK_EASYLIST, stream=True)) as file:
			lines = 0 # to be removed
			for rule in file.iter_lines():
				raw_rules.append(rule.strip())
				lines += 1 # tbr
				if lines == 2500: break # tbr, only for windoze with no re2
		rules = AdblockRules(raw_rules)
		return rules

	rules = get_rules() # static

	def __call__(self, url):
		if AdblockURLFilter.rules.should_block(url):
			print "[BadImage] AdblockURLFilter: %s" % url
			return None
		return url

# from cStringIO import StringIO
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
		length = 0
		raw_image = None
		with closing(requests.get(url, stream=True)) as response:
			response.raise_for_status()
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
		image = Image(response.url, raw_image.size, raw_image.format)
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
IMAGE_MIN_IMGSIZE = (48, 48)
IMAGE_MAX_IMGSIZE = (2048, 2048)

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
		if  ratio < 1 / IMAGE_LIMIT_RATIO or \
			ratio > IMAGE_LIMIT_RATIO:
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


class MonoImageFilter(object): # SizeImageFilter
	"""
	Checks whether the image is (plain black or) white and returns None.
	Otherwise return the Image instance.
	http://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
	"""
	def __call__(self, image):
		# image = super(MonoImageFilter, self).__call__(image)
		try:
			# sum(img.convert("L").getextrema()) in (0, 2)
			if image.raw.convert("L").getextrema() == (1, 1):
				print "[BadImage] MonoImageFilter: %s" % image.url
				return None
		except Exception, e:
			print "[BadImage] %s: %s" % (clsn(e), image.url)
			return image



