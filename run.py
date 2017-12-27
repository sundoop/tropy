#!/usr/bin/python
# filename: run.py
import logging

from tropy import trope_cache, trope_extractor

def run(url='http://tvtropes.org'):

    urls = [
            'http://tvtropes.org/pmwiki/pmwiki.php/Literature/TheMartian',
            'http://tvtropes.org/pmwiki/pmwiki.php/Film/TheMartian',
            'http://tvtropes.org/pmwiki/pmwiki.php/Film/WonderWoman2017',
            ]

    tropes = []
    for url in urls:
        tropes.extend(trope_extractor.TropeExtractor.get_from_url(url))

    return tropes

def get_trope_store():
    tc = trope_cache.TropeStore()
    return tc

def setup_logging():
    logger = logging.getLogger('tropy')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('logging.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

logger = setup_logging()
if __name__ == "__main__":
    run('http://tvtropes.org/pmwiki/pmwiki.php/Film/Bright')
