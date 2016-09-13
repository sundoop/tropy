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
            te.Trope('FooBar', 'Foo Bar', 'http://tvtropes.org/pmwiki/pmwiki.php/Main/FooBar'),

            te.Trope('BarFoo', 'Bar Foo', 'http://tvtropes.org/pmwiki/pmwiki.php/Main/BarFoo')
        ]
        tropes = te.TropeExtractor._get_tropes_from_soup(test_soup)
        self.assertListEqual(tropes, expected_tropes)
