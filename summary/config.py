"""
Summary config settings.
These can be overwritten after importing `summary` and before using it.
"""
def from_object(updates):
    "Update same name (or prefixed) settings."
    import sys
    config = sys.modules[__name__]
    
    prefix = config.__name__.split('.')[0].upper()
    keys = [k for k in config.__dict__ if \
        k != from_object.__name__ and not k.startswith('_')]
    get_value = lambda c, k: hasattr(c, k) and getattr(c, k) or None
    for key in keys:
        prefix_key = '%s_%s' % (prefix, key)
        value = get_value(updates, prefix_key) or get_value(updates, key)
        if value: setattr(config, key, value)

### Package settings ###

USER_AGENT = 'summary-extraction 0.2'
# USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
ENCODING = 'utf-8' # None for autodetect
TIMEOUT = (10, 10) # (connect, read) # None for never

CHUNK_SIZE = 1024 # 1 KB
HTML_MAX_BYTESIZE = 2 * 1048576 # 1 MB

GET_ALL_DATA = False # for better performance
# MAX_ITEMS = 2 # to choose from

# URL query keys to keep
USEFUL_QUERY_KEYS = [
    'id',
]

# PhantomJS
PHANTOMJS_BIN = '' # '/usr/local/bin/phantomjs'
PHANTOMJS_SITES = [
    'readwrite.com',
]

# Noncanonic sites
NONCANONIC_SITES = [
    'www.google.com',
]


### Filters settings ###

# AdblockURLFilter
ADBLOCK_EASYLIST_URL = 'easylist.txt'
    # 'https://easylist-downloads.adblockplus.org/easylist.txt'
ADBLOCK_EXTRALIST_URL = 'extralist.txt' 
    # 'https://dl.dropboxusercontent.com/u/134594/svven/extralist.txt'

# NoImageFilter
IMAGE_MAX_BYTESIZE = 1 * 1048576 # 1 MB

# SizeImageFilter
IMAGE_LIMIT_RATIO = 3.6 # if js crop center square
IMAGE_MIN_IMGSIZE = (75, 75)
IMAGE_MAX_IMGSIZE = (2064, 2064)

# MonoImageFilter
IMAGE_MONO_RULE = r'((_|\b)(white|blank|black|overlay)(_|\b))'
