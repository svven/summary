"This file contains filters for the extracted data, mainly images."

# from PIL.Image import Image as PILImage
# from PIL.ImageFile import Parser as PILParser

# CHUNK_SIZE = 1024 # 1 KB
# MAX_SIZE = 2 * 1048576 # 2 MB
# MIN_IMGSIZE = (30, 30)
# MAX_IMGSIZE = (1024, 768)


class ZeroBytesError(Exception):
	pass

class MaxBytesError(Exception):
	pass


class Image(object):
	"Used by the filter classes below."
	def __init__(self, url):
		self.url = url
	
	def __repr__(self):
		return self.url


class AdblockURLFilter(object): # Filter
	"Uses Adblock URL filtering and returns None if should_block."
	def __call__(self, url):
		if 'doubleclick.net' in url:
			print "[BadImage] AdblockURLFilter: %s" % url
			return None
		return url


class NoImageFilter(object): # AdblockURLFilter
	"""
	Retrieves actual image and returns it, or None if it fails.
	Returns instance of Image class to be verified by following filters.
	"""
	def __call__(self, url):
		# url = super(NoImageFilter, self).__call__(url)
		return Image(url)

class SizeImageFilter(object): # NoImageFilter
	"""
	Checks image to have proper size, or returns None if it doesn't.
	This may rule out tracking images that were not detected by AdblockURLFilter.
	"""
	def __call__(self, image):
		# image = super(SizeImageFilter, self).__call__(image)
		return image

class MonoImageFilter(object): # SizeImageFilter
	"""
	Checks whether the image is plain black or white and returns None.
	Otherwise return the Image instance.
	"""
	def __call__(self, image):
		# image = super(MonoImageFilter, self).__call__(image)
		return image



