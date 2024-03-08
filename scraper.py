import requests
import time
import bs4
import urllib
import urllib3

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'


def _req(term, results, lang, start, proxies, timeout):
    resp = requests.get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": USER_AGENT
        },
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
        },
        proxies=proxies,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"

class Scraper:
    def __init__(self, query=None) -> None:
        self.query = query

    @property
    def result(self):
        return self.search(self.query)

    def search(self, term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5):
        """Search the Google search engine"""

        self.query = term
        previously_yielded = []
        escaped_term = urllib.parse.quote_plus(term)

        # Proxy
        proxies = None
        if proxy:
            if proxy.startswith("https"):
                proxies = {"https": proxy}
            else:
                proxies = {"http": proxy}

        # Fetch
        start = 0
        # while start < num_results:
        # Send request
        resp = _req(escaped_term, num_results - start,
                    lang, start, proxies, timeout)

        # Parse
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        if len(result_block) ==0:
            start += 1
        for result in result_block:
            # Find link, title, description
            link = result.find("a", href=True)
            hostname = urllib3.util.parse_url(link['href']).hostname

            title = result.find("h3")
            description_box = result.find(
                "div", {"style": "-webkit-line-clamp:2"})
            if description_box:
                description = description_box.text
                if link and title and description:
                    if hostname.count('.') == 1:
                        if hostname in previously_yielded:
                            continue
                        else:
                            previously_yielded.append(hostname)
                    else:
                        master = hostname.split('.', 1)[1]
                        if master in previously_yielded:
                            continue
                        else:
                            previously_yielded.append(master)

                    start += 1
                    if advanced:
                        yield SearchResult(link["href"], title.text, description)
                    else:
                        yield link["href"]
        time.sleep(sleep_interval)

        if start == 0:
            return []
    
    def content_search(self, term, num_results=10, lang='en', proxy=None, advanced=False, sleep_interval=0, timeout=5):
        results = self.search(term, num_results=num_results, lang=lang, proxy=proxy, advanced=advanced, sleep_interval=sleep_interval, timeout=timeout)
        items = [res for res in results]

        return items

def validity_check(elem):
    return elem.text.strip()

def text_from_html(contents, *, limit=10):
    soup = bs4.BeautifulSoup(contents, 'html.parser')
    texts = soup.find_all('p', class_=lambda cls: (cls != 'interlanguage-link-target'))
    yield from list(filter(validity_check, texts))[:limit]
