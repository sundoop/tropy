import os
import sqlite3
import unittest

from tropy import trope_cache as tc
from tropy import trope_extractor as te


class TestTropeCache(unittest.TestCase):

    def setUp(self):
        self.test_db_name = 'test_db_name.db'

    def tearDown(self):
        try:
            os.remove(self.test_db_name)
        except OSError:
            pass

    def _get_conn_to_test_db(self):
        return sqlite3.connect(self.test_db_name)

    def test_initialization_of_cache_creates_a_db_file(self):
        tc.TropeStore(db_file=self.test_db_name)
        self.assertTrue(os.path.exists(self.test_db_name))

    def test_cache_creation_creates_an_empty_table(self):
        tc.TropeStore(db_file=self.test_db_name)

        CHECKTABLE_SQL = "SELECT name FROM sqlite_master WHERE type='table' AND name='tropes';"

        c = self._get_conn_to_test_db().cursor()
        self.assertTrue(c.execute(CHECKTABLE_SQL))

    def test_set_trope_and_get_it(self):
        cache = tc.TropeStore(self.test_db_name)

        trope = te.Trope('fooID', 'fooType', 'fooName', 'fooUrl', 'fooContent')
        cache.set_trope(trope)
        retrieved_trope = cache.get_trope('fooUrl')

        self.assertEqual(trope, retrieved_trope)

    def test_set_trope_for_identical_tropes_ok(self):

        cache = tc.TropeStore(self.test_db_name)
        trope = te.Trope('fooID', 'fooType', 'fooName', 'fooUrl', 'fooContent')

        cache.set_trope(trope)
        cache.set_trope(trope)

    def test_get_missing_trope_returns_empty_trope(self):

        cache = tc.TropeStore(self.test_db_name)

        empty_trope = te.Trope()
        retrieved_trope = cache.get_trope(url='foobar')

        self.assertEqual(retrieved_trope, empty_trope)

    def test_set_trope_ids(self):
        cache = tc.TropeStore(self.test_db_name)

        tropes = [
            te.Trope('fooID', 'fooType', 'fooName', 'fooUrl', 'fooContent'),
            te.Trope('barID', 'fooType', 'fooName', 'fooUrl', 'fooContent'),
            te.Trope('bazID', 'fooType', 'fooName', 'fooUrl', 'fooContent')
        ]
        for trope in tropes:
            cache.set_trope(trope)

        ids = set(cache.get_all_trope_ids())
        expected_ids = set([t.id for t in tropes])
        self.assertSetEqual(ids, expected_ids)

    def test_get_all_urls_without_content(self):
        cache = tc.TropeStore(self.test_db_name)

        tropes = [
            te.Trope('fooID', 'fooType', 'fooName', 'fooUrl', 'fooContent'),
            te.Trope('barID', 'fooType', 'fooName', 'barUrl', ''),
            te.Trope('bazID', 'fooType', 'fooName', 'bazUrl', 'fooContent'),
            te.Trope('pooID', 'fooType', 'fooName', 'pooUrl', '')
        ]
        for trope in tropes:
            cache.set_trope(trope)

        urls_with_no_content = set(cache.get_all_urls_without_content())
        self.assertSetEqual(urls_with_no_content, set(['barUrl', 'pooUrl']))
