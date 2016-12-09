import collections
import mock
import unittest

from tropy import trope_extractor as te

MockResponse = collections.namedtuple('Response', 'status_code text')


class TestBasePageHandlerGetHtmlContent(unittest.TestCase):

    def test_with_empty_page_url(self):
        dummy_url = ''
        html_content = te.BasePageHandler._get_html_content(dummy_url)
        self.assertEqual(html_content, '')

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_valid_response(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse(te.requests.codes.ok, 'dummy value')
        html_content = te.BasePageHandler._get_html_content(dummy_url)
        self.assertTrue(html_content, 'dummy value')

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_invalid_status_code(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse('not_ok', 'dummy value')
        with self.assertRaises(te.TvTropeConnectionError):
            te.BasePageHandler._get_html_content(dummy_url)

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_missing_content(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse(te.requests.codes.ok, None)
        with self.assertRaises(te.MissingContentError):
            te.BasePageHandler._get_html_content(dummy_url)


class TestBasePageHandlerGetFromUrl(unittest.TestCase):

    def test_with_empty_page_url_returns_empty_list(self):
        test_page_url = ''
        tropes = te.BasePageHandler.get_from_url(test_page_url)
        self.assertListEqual([], tropes)

    @mock.patch.object(te.BasePageHandler, '_get_html_content')
    @mock.patch.object(te.BasePageHandler, '_get_items_from_soup')
    @mock.patch.object(te, 'BeautifulSoup')
    def test_with_page_url(self, mock_soup, mock_get_tropes, mock_get_html):
        test_page_url = 'dummy_url'
        tropes = te.BasePageHandler.get_from_url(test_page_url)

        # html content retrieved using page_url
        mock_get_html.assert_called_with(test_page_url)
        # soup generated from html_content
        mock_soup.assert_called_with(mock_get_html.return_value, 'html.parser')
        # tropes retrieved from soup
        mock_get_tropes.assert_called_with(mock_soup.return_value)

        self.assertEqual(tropes, mock_get_tropes.return_value)

    @mock.patch.object(te.requests, "get")
    def test_for_ConnectionError(self, mock_get):
        test_page_url = 'dummy_url'
        mock_get.return_value = MockResponse(400, 'mock_response_text')

        actual = te.BasePageHandler.get_from_url(test_page_url)
        self.assertListEqual([], actual)

    @mock.patch.object(te.requests, "get")
    def test_for_ContentError(self, mock_get):
        test_page_url = 'dummy_url'
        mock_get.return_value = MockResponse(200, None)

        actual = te.BasePageHandler.get_from_url(test_page_url)
        self.assertListEqual([], actual)

    @mock.patch.object(te.BasePageHandler, "_get_html_content")
    def test_for_ContentParsingError(self, mock_get):
        test_page_url = 'dummy_url'
        mock_get.side_effect = te.ContentParsingError

        actual = te.BasePageHandler.get_from_url(test_page_url)
        self.assertListEqual([], actual)

    @mock.patch.object(te.BasePageHandler, '_get_html_content')
    @mock.patch.object(te.BasePageHandler, '_get_items_from_soup')
    @mock.patch.object(te, 'BeautifulSoup')
    def test_for_ParsingError(self, mock_soup, mock_get_items, mock_get_html):
        test_page_url = 'dummy_url'

        # cause soup parsing to throw up
        mock_soup.return_value.find.side_effect = Exception

        # should be handled, and an empty list should be returned
        actual = te.BasePageHandler.get_from_url(test_page_url)
        self.assertEqual(mock_get_items.return_value, actual)


class TestBasePageHandlerGetItemsFromSoup(unittest.TestCase):

    def test_basehandler_get_items_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            mock_soup = mock.MagicMock()
            te.BasePageHandler._get_items_from_soup(mock_soup)
