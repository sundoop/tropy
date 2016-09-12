import collections
import mock
import unittest

from bs4 import BeautifulSoup
from tropy import trope_extractor as te

MockResponse = collections.namedtuple('Response', 'status_code text')


class TestTropeExtractorGetHtmlContent(unittest.TestCase):

    def test_with_empty_page_url(self):
        dummy_url = ''
        html_content = te.TropeExtractor._get_html_content(dummy_url)
        self.assertEqual(html_content, '')

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_valid_response(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse(te.requests.codes.ok, 'dummy value')
        html_content = te.TropeExtractor._get_html_content(dummy_url)
        self.assertTrue(html_content, 'dummy value')

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_invalid_status_code(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse('not_ok', 'dummy value')
        with self.assertRaises(te.TvTropeConnectionError):
            te.TropeExtractor._get_html_content(dummy_url)

    @mock.patch.object(te.requests, "get")
    def test_get_html_content_for_missing_content(self, mock_get):
        dummy_url = 'mock_url'
        mock_get.return_value = MockResponse(te.requests.codes.ok, None)
        with self.assertRaises(te.MissingContentError):
            te.TropeExtractor._get_html_content(dummy_url)


HTML_WITH_MISSING_PAGE_CONTENT_DIV = """
<div class='foo-class'></div>
"""

HTML_WITH_MISSING_TWIKI_LINKS = """
<div class='page-content'></div>
"""

STANDARD_HTML = """
<div class='page-content'>
    <ul>
        <li>
    <a class="twikilink" href="http://tvtropes.org/pmwiki/pmwiki.php/Main/FooBar"
    title="http://tvtropes.org/pmwiki/pmwiki.php/Main/FooBar">Foo Bar</a>
        </li>
        <li>
        <a class="twikilink" href="http://tvtropes.org/pmwiki/pmwiki.php/Main/BarFoo"
        title="http://tvtropes.org/pmwiki/pmwiki.php/Main/BarFoo">Bar Foo</a>
        </li>
    </ul>
</div>
""".replace('\n', '')


class TestTropeExtractorGetTropesFromSoup(unittest.TestCase):

    def test_with_empty_soup(self):
        test_soup = ''
        self.assertEqual([], te.TropeExtractor._get_tropes_from_soup(test_soup))

    def test_missing_content_div_throws_up(self):
        test_soup = BeautifulSoup(HTML_WITH_MISSING_PAGE_CONTENT_DIV, 'html.parser')
        with self.assertRaises(te.ContentParsingError):
            te.TropeExtractor._get_tropes_from_soup(test_soup)

    def test_missing_twikis_returns_empty_list(self):
        test_soup = BeautifulSoup(HTML_WITH_MISSING_TWIKI_LINKS, 'html.parser')
        tropes = te.TropeExtractor._get_tropes_from_soup(test_soup)
        self.assertListEqual(tropes, [])

    def test_with_standard_soup(self):
        test_soup = BeautifulSoup(STANDARD_HTML, 'html.parser')
        expected_tropes = [
            te.Trope('FooBar', 'Foo Bar', 'http://tvtropes.org/pmwiki/pmwiki.php/Main/FooBar'),

            te.Trope('BarFoo', 'Bar Foo', 'http://tvtropes.org/pmwiki/pmwiki.php/Main/BarFoo')
        ]
        tropes = te.TropeExtractor._get_tropes_from_soup(test_soup)
        self.assertListEqual(tropes, expected_tropes)


class TestGetTropesFromPage(unittest.TestCase):

    def test_with_empty_page_url_returns_empty_list(self):
        test_page_url = ''
        tropes = te.TropeExtractor.get_tropes_from_page(test_page_url)
        self.assertListEqual([], tropes)

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    @mock.patch.object(te.TropeExtractor, '_get_tropes_from_soup')
    @mock.patch.object(te, 'BeautifulSoup')
    def test_with_page_url(self, mock_soup, mock_get_tropes, mock_get_html):
        test_page_url = 'dummy_url'
        tropes = te.TropeExtractor.get_tropes_from_page(test_page_url)

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

        actual = te.TropeExtractor.get_tropes_from_page(test_page_url)
        self.assertListEqual([], actual)

    @mock.patch.object(te.requests, "get")
    def test_for_ContentError(self, mock_get):
        test_page_url = 'dummy_url'
        mock_get.return_value = MockResponse(200, None)

        actual = te.TropeExtractor.get_tropes_from_page(test_page_url)
        self.assertListEqual([], actual)

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    @mock.patch.object(te, 'BeautifulSoup')
    def test_for_ParsingError(self, mock_soup, mock_get_html):
        test_page_url = 'dummy_url'

        # cause soup parsing to throw up
        mock_soup.return_value.find.side_effect = Exception

        # should be handled, and an empty list should be returned
        actual = te.TropeExtractor.get_tropes_from_page(test_page_url)
        self.assertListEqual([], actual)
