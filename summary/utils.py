def convert(mystr, encoding):
    if isinstance(mystr, unicode):
        return mystr
    else:
        return mystr.decode(encoding, 'ignore')
