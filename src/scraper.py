import requests
import bs4
import utils
import typing

def text_similarity(a: str, b: str) -> float:
    """
        Gets the Levenshtein distance between 2 strings

        :param a: The first string
        :param b: The second string
        :returns: The Levenshtein distance between string `a` and `b`
    """
    if len(b) == 0: return len(a)
    if len(a) == 0: return len(b)
    if a[0] == b[0]: return text_similarity(a[1:], b[1:])
    return 1 + min([
        text_similarity(a[1:], b),
        text_similarity(a, b[1:]),
        text_similarity(a[1:], b[1:])
    ])

def columbia_encyclopedia(host_scheme: str, query: str, *, limit: int = 1) -> typing.Generator[str, None, list]:
    """
        Scrapes data from Columbia Encyclopedia regarding the query
        
        :param host_scheme: The host url of Columbia Encyclopedia (https://www.infoplease.com)
        :param query: The query to search for
        :param limit: The number of results to return
        :returns: A generator of the contents of relevant pages
    """
    def loose_search() -> typing.Generator[str, None, list]:
        """
            Searches the encyclopedia to get links to relevant pages

            :returns: A generator of sub-links. Eg. /ice-cream
        """
        url = f'{host_scheme.strip("/")}/search/encyclopedia/{"+".join(query.lower().split())}'
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
        iterator = iter(soup.find_all('article', class_='contextual-region'))
        for _ in range(limit):  # Yield only `limit` number of links or fewer
            a = next(iterator).h2.a
            if text_similarity(a.text, query) < 5:
                yield a['href']
            else:
                return []

    try:
        for href in loose_search():
            url = f'{host_scheme.strip("/")}/{href.strip("/")}'  # Constructed page url
            yield bs4.BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='article-detail')[0].div.p.text.strip()
    except RuntimeError:
        return []

def wikipedia(host_scheme: str, query: str, *, limit: int = 1) -> typing.Generator[str, None, None]:
    """
        Scrapes data from Wikipedia regarding the query
        
        :param host_scheme: The host url of Wikipedia (https://en.wikipedia.org)
        :param query: The query to search for
        :param limit: The number of results to return
        :returns: A generator of the contents of relevant pages
    """
    def empty_filter(content) -> str:
        # Returns the text of a tag, empty string if the content is empty or spaces.
        return content.text.strip()

    def loose_search() -> tuple[list[str], int]:
        """
            Searches wikipedia to get links to relevant pages

            :returns: A list of sub-links, and a number denoting whether we got redirected or not.
        """
        url = f"{host_scheme.strip('/')}/wiki/Special:Search?search={'+'.join(query.lower().split())}&ns0=1"
        resp = requests.head(url, allow_redirects=True)
        if resp.url != url:  # We got redirected!
            url = resp.url
            return ( 
                list(filter(empty_filter, bs4.BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='mw-content-ltr')[0].find_all('p')))[:limit],
                1
            )
        else:
            soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
            iterator = iter(soup.find_all('div', class_='mw-search-result-heading'))
            return [next(iterator).a['href']for _ in range(limit)], 0

    contents, redirected = loose_search()
    if redirected:
        for content in contents:
            yield empty_filter(content)
    else:
        for href in contents:
            url = f'{host_scheme.strip("/")}/{href.strip("/")}'
            yield bs4.BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='mw-content-ltr')[0].p.text.strip()


class ScrapeSite:
    def __init__(self, host_scheme: str, search_on: typing.Callable = None) -> None:
        self.host_scheme = host_scheme
        self.search_on = search_on  # Search function

    def fetch(self, query: str, *, limit: int = 1) -> typing.Generator[str, None, list]:
        """
            Fetches result from its respective site.

            :param query: The query to search for
            :param limit: The number of pages to search
            :returns: A generator of contents of relevant pages
        """
        yield from self.search_on(self.host_scheme, query, limit=limit)

class Scraper:
    def __init__(self, scrapers: list[ScrapeSite] = None) -> None:
        self.scrapers = scrapers or \
            [ScrapeSite('https://www.infoplease.com', columbia_encyclopedia), ScrapeSite('https://en.wikipedia.org', wikipedia)]

    def fetch_results(self, query: str, *, limit: int = 1) -> list[str]:
        """
            Gets contents relevant to the query from all the ScrapeSites

            :param query: The query to search for
            :param limit: The number of pages to search
            :returns: A list of contents from all the ScrapeSites
        """
        while True:
            try:
                results: list[str] = []
                for scraper_idx in utils.Bar(range(len(self.scrapers)), 'sites searched', 'Searching complete.'):
                    for result in self.scrapers[scraper_idx].fetch(query, limit=limit):
                        results.append(result)

                return results
            except KeyboardInterrupt:
                # User hit ^C, end the program is they enter something, restart the searching if they don't.
                if not input("\nDon't enter anything to continue: "):
                    continue
                return
