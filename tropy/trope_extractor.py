import attr
import logging
import re
import requests

from bs4 import BeautifulSoup


@attr.s
class Trope(object):
    """
    temp class to hold a trope
    """

    id = attr.ib()
    name = attr.ib()
    url = attr.ib()
    content = attr.ib(default=None)


class BasePageHandler(object):
    """
    base methods for handling pages
    """
    @classmethod
    def _get_html_content(cls, page_url):
        """
        retrieve the html content from a trope's page url
        """
        if not page_url:
            return ''

        resp = requests.get(page_url)

        if resp.status_code != requests.codes.ok:
            raise TvTropeConnectionError(
                "recieved code:%s for url:%s" % (resp.status_code, page_url)
            )

        if not resp.text:
            raise MissingContentError(
                "recieved no html for url:%s" % (page_url)
            )

        return resp.text

    @classmethod
    def get_from_url(cls, page_url):
        """
        get items, given a url
        """

        logging.info("attempting to get items for url: %s", page_url)
        if not page_url:
            logging.info("empty url... bailing")
            return []

        try:

            # get the html content from a page
            html_content = cls._get_html_content(page_url)
            logging.debug('got content:%s from url:%s', html_content, page_url)

            # convert to beautiful, beautiful soup
            soup = BeautifulSoup(html_content, 'html.parser')
            logging.debug('got soup:%s from url:%s', soup, page_url)

            # get tropes from the html_content
            items = cls._get_items_from_soup(soup)

            return items

        except TvTropeConnectionError:
            logging.error("error connecting to tvtropes!")

        except MissingContentError:
            logging.error("tvtropes returned null content!")

        except ContentParsingError:
            logging.error("error parsing content!")

        return []

    @classmethod
    def _get_items_from_soup(cls, soup):
        """
        BasePageHandler shouldn't implement this method
        """
        logging.exception("BasePageHandler's _get_items_from_soup called!")
        raise NotImplementedError()


class TropeExtractor(BasePageHandler):
    """
    Helper to extract tropes from a page
    """

    @classmethod
    def get_tropes_from_page(cls, page_url):
        """
        extract tropes given a page
        """
        logging.info("attempting to get tropes for url: %s", page_url)
        return cls.get_from_url(page_url)

    @classmethod
    def _get_items_from_soup(cls, soup):
        return cls._get_tropes_from_soup(soup)

    @classmethod
    def _get_tropes_from_soup(cls, soup):
        """
        extract tropes given a BeautifulSoup soup object
        """

        if not soup:
            return []

        try:
            # there's going to be some experimentation here, to figure out the extraction
            # extract the div containing the trope content
            content_div = soup.find('div', class_=TvTropePageConstants.PAGE_CONTENT_CLASS)

            # extract the tropes from this div wonly
            trope_links = content_div.find_all(
                class_=TvTropePageConstants.TWIKILINK_CLASS,
                href=re.compile(TvTropePageConstants.URL_PREFIX_FOR_TROPE_LINKS)
            )

            tropes = []
            for tl in trope_links:
                try:
                    t_id = tl.get('href').split('/')[-1]
                    name = tl.string
                    url = tl.get('href')
                    tropes.append(
                        Trope(id=t_id, name=name, url=url, content=None)
                    )
                except Exception:
                    logging.exception('error processing trope link:%s', tl)
        except Exception:
            logging.exception('error parsing soup')
            raise ContentParsingError('error parsing soup:%s' % soup)
        return tropes


class TvTropePageConstants(object):
    """
    css class names as constants
    """
    PAGE_TITLE_CLASS = 'page-title'
    TWIKILINK_CLASS = 'twikilink'
    PAGE_CONTENT_CLASS = 'page-content'
    URL_PREFIX_FOR_TROPE_LINKS = 'tvtropes.org/pmwiki/pmwiki.php/Main/'


class TvTropeConnectionError(Exception):
    pass


class MissingContentError(Exception):
    pass


class ContentParsingError(Exception):
    pass
