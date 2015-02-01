import os

import mock
from mock import MagicMock
from requests import Response

from summary import Summary


@mock.patch('summary.request.get')
def test_summary(mock_request):

    # Given
    url = 'http://www.google.com'
    mock_response = Response()
    mock_response.headers.get = MagicMock(return_value = 'html')
    mock_response.url = url
    mock_response.encoding = 'UTF-8'
    mock_response.consumed = True
    mock_response.raw = MagicMock()
    mock_request.return_value = mock_response

    # When
    summ = Summary(url)
    summ._html = '<html><head><title>Test Title</head><body></body></html>'
    summ.extract()

    # Then
    # mock_response.raw.close.assert_called_with()
    assert summ.title == 'Test Title'


def get_test_data(test):
    testfile = './test_data_' + str(test) + '.txt'
    testpath = os.path.join(os.path.dirname(__file__), testfile)
    with open (testpath, 'r') as myfile:
        data = myfile.read()
    return data