import collections
import mock
import unittest

from bs4 import BeautifulSoup
from tropy import trope_extractor as te

MockResponse = collections.namedtuple('Response', 'status_code text')


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
    <input type="hidden" id="groupname-hidden" value="Film"/>
    <input type="hidden" id="title-hidden" value="FooBar"/>
</div>
""".replace('\n', '')

ERROR_HTML = """
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
    <input type="hidden" id="groupname-hidden" value="Film"/>
</div>
""".replace('\n', '')


class TestTropeExtractorGetTropesFromSoup(unittest.TestCase):

    def test_with_empty_soup(self):
        test_soup = ''
        self.assertEqual([], te.TropeExtractor._get_tropes_from_soup(test_soup))

    @mock.patch.object(te.BasePageHandler, 'get_from_url')
    def test_get_tropes_calls_base_method(self, mock_base_get):
        test_url = 'foo_bar'
        te.TropeExtractor.get_tropes_from_page(test_url)
        mock_base_get.assert_called_with(test_url)

    @mock.patch.object(te.TropeExtractor, '_get_tropes_from_soup')
    def test_get_items_calls_get_tropes(self, mock_get_tropes):
        test_soup = 'test_soup'
        te.TropeExtractor._get_items_from_soup(test_soup)
        mock_get_tropes.assert_called_with(test_soup)

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
            te.Trope(id='FooBar', name='Foo Bar', url='http://tvtropes.org/pmwiki/pmwiki.php/Main/FooBar', content=''),

            te.Trope(id='BarFoo', name='Bar Foo', url='http://tvtropes.org/pmwiki/pmwiki.php/Main/BarFoo', content='')
        ]
        tropes = te.TropeExtractor._get_tropes_from_soup(test_soup)
        self.assertListEqual(tropes, expected_tropes)


class TestTropeExtractorGetTropeDetails(unittest.TestCase):
    """
    Test Suite for TropeExtractor._get_trope_details
    """

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    def test_get_trope_details_retrieves_html_for_url(self, mock_get_html_getter):

        mock_get_html_getter.return_value = STANDARD_HTML

        test_page_url = 'test_page_url'
        te.TropeExtractor._get_trope_details(test_page_url)

        mock_get_html_getter.assert_called_with(test_page_url)

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    def test_get_trope_details_retrieves_a_trope(self, mock_get_html_getter):

        mock_get_html_getter.return_value = STANDARD_HTML

        test_page_url = 'test_page_url'
        expected_trope = te.TropeExtractor._get_trope_details(test_page_url)

        self.assertEqual(expected_trope.id, 'FooBar')
        self.assertEqual(expected_trope.type, 'Film')
        self.assertEqual(expected_trope.name, '')
        self.assertEqual(expected_trope.url, test_page_url)

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    def test_get_trope_details_throws_for_bad_html(self, mock_get_html_getter):

        mock_get_html_getter.return_value = ERROR_HTML

        test_page_url = 'test_page_url'
        with self.assertRaises(te.MissingContentError):
            te.TropeExtractor._get_trope_details(test_page_url)


class TestTropeExtractorGetTropeFromURL(unittest.TestCase):
    """
    Test suite for TropeExtractor.get_trope_from_url
    """

    def test_get_trope_details_with_invalid_url(self):
        with self.assertRaises(ValueError):
            te.TropeExtractor.get_trope_from_url('invalid_url')

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    def test_get_trope_details_for_valid_url_with_invalid_content(self, mock_html_getter):
        mock_html_getter.return_value = ERROR_HTML
        expected_trope = te.Trope()
        actual_trope = te.TropeExtractor.get_trope_from_url('http://tvtropes.org/foo')
        self.assertEqual(expected_trope, actual_trope)

    @mock.patch.object(te.TropeExtractor, '_get_html_content')
    def test_get_trope_details_for_valid_url_with_valid_content(self, mock_html_getter):
        mock_html_getter.return_value = STANDARD_HTML
        page_url = 'http://tvtropes.org/foo'
        expected_trope = te.Trope(id='FooBar', type='Film', url=page_url, content=STANDARD_HTML)
        actual_trope = te.TropeExtractor.get_trope_from_url(page_url)
        self.assertEqual(expected_trope, actual_trope)
