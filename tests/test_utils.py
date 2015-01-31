# -*- coding: utf-8 -*-

import string

from summary.utils import convert


def test_happy_uni_already():
    # Given
    encoding = "UTF-8"
    unicode_str = unicode("Test ¬¬ƒßø∂~≈^", encoding)

    # When
    results = convert(unicode_str, encoding)

    # Then
    assert (isinstance(results, unicode))

def test_happy_ascii_to_uni():
    # Given
    encoding = "UTF-8"
    normal_str = string.ascii_letters.encode('ascii', 'ignore')

    # When
    results = convert(normal_str, encoding)

    # Then
    assert (not isinstance(normal_str, unicode))
    assert (isinstance(results, unicode))
