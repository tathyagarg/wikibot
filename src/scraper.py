import requests
import bs4
import utils

def text_similarity(a, b):
    if len(b) == 0: return len(a)
    if len(a) == 0: return len(b)
    if a[0] == b[0]: return text_similarity(a[1:], b[1:])
    return 1 + min([
        text_similarity(a[1:], b),
        text_similarity(a, b[1:]),
        text_similarity(a[1:], b[1:])
    ])

def columbia_encyclopedia(host_scheme, query, *, limit=1):
    def loose_search():
        url = f'{host_scheme.strip("/")}/search/encyclopedia/{"+".join(query.lower().split())}'
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
        iterator = iter(soup.find_all('article', class_='contextual-region'))
        for _ in range(limit):
            a = next(iterator).h2.a
            if text_similarity(a.text, query) < 5:
                yield a['href']
            else:
                return []

    try:
        for href in loose_search():
            url = f'{host_scheme.strip("/")}/{href.strip("/")}'
            yield bs4.BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='article-detail')[0].div.p.text.strip()
    except RuntimeError:
        return []

def wikipedia(host_scheme, query, *, limit=1):
    def empty_filter(content):
        return content.text.strip()

    def loose_search():
        url = f"{host_scheme.strip('/')}/wiki/Special:Search?search={'+'.join(query.lower().split())}&ns0=1"
        resp = requests.head(url, allow_redirects=True)
        if resp.url != url:
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
            yield content.text.strip()
    else:
        for href in contents:
            url = f'{host_scheme.strip("/")}/{href.strip("/")}'
            yield bs4.BeautifulSoup(requests.get(url).text, 'html.parser').find_all('div', class_='mw-content-ltr')[0].p.text.strip()


class ScrapeSite:
    def __init__(self, host_scheme, search_on = None) -> None:
        self.host_scheme = host_scheme
        self.search_on = search_on

    def fetch(self, query, *, limit=1):
        yield from self.search_on(self.host_scheme, query, limit=limit)

class Scraper:
    def __init__(self, scrapers=None) -> None:
        self.scrapers = scrapers or [ScrapeSite('https://www.infoplease.com', columbia_encyclopedia), ScrapeSite('https://en.wikipedia.org', wikipedia)]        

    def fetch_results(self, query, *, limit=1):
        while True:
            try:
                results = []
                for scraper_idx in utils.Bar(range(len(self.scrapers)), 'sites searched', 'Searching complete.'):
                    for result in self.scrapers[scraper_idx].fetch(query, limit=limit):
                        results.append(result)

                return results
            except KeyboardInterrupt:
                if not input("\nDon't enter anything to continue: "):
                    continue
                return
