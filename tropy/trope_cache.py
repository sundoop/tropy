import datetime
import logging
import sqlite3

from tropy import trope_extractor


class TropeStore(object):
    """
    Persist trope data
    """

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS tropes
    (id text PRIMARY KEY, type text, name text, url text, content text);
    """

    def __init__(self, db_file=None):
        if not db_file:
            db_file = 'store_run_%s.db' % str(datetime.datetime.utcnow()).replace(' ', '-').split('.')[0]
        self.conn = sqlite3.connect(db_file)
        c = self.conn.cursor()
        c.execute(self.CREATE_TABLE_SQL)
        self.conn.commit()
        self.cursor = self.conn.cursor()

        self.logger = logging.getLogger('tropy.tropeStore')

    def set_trope(self, trope):
        try:
            self.cursor.execute(
                "INSERT INTO tropes VALUES(?, ?, ?, ?, ?)",
                (trope.id, trope.type, trope.name, trope.url, trope.content)
            )
        except sqlite3.IntegrityError:
            self.logger.info("error inserting trope:%s into store", trope)
        self.conn.commit()

    def get_trope(self, url):
        trope = trope_extractor.Trope()
        self.cursor.execute("SELECT id, type, name, url, content FROM tropes where url=?", (url,))
        row = self.cursor.fetchone()
        if row:
            trope = trope_extractor.Trope(
                id=row[0], type=row[1], name=row[2],
                url=row[3], content=row[4]
            )
        return trope

    def get_all_trope_ids(self):
        self.cursor.execute("SELECT id from tropes")
        rows = [r[0] for r in self.cursor.fetchall()]
        return rows

    def get_all_urls_without_content(self):
        self.cursor.execute("SELECT url from tropes where content = '';")
        rows = self.cursor.fetchall()
        urls = [r[0] for r in rows]
        return urls
