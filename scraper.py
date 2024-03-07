import re
import toml
import utils
import os
from urllib.parse import urlparse, urlunparse, unquote
from urllib3.util import parse_url
from urllib3.poolmanager import proxy_from_url
from base64 import b64encode

def fetch_version() -> str:
    with open(utils.CONFIG_LOCATION, 'r') as f:
        config = toml.load(f)
    return config['version']

DEFAULT_HEADERS = {
    'user-agent': f"wikibot/{fetch_version()}",
    'accept-encoding': ", ".join(re.split(r',\s*', "gzip,deflate")),
    'accept': "*/*",
    'connection': 'keep-alive'
}

DEFAULT_HOOKS = {"response": []}
REDIRECT_LIMIT = 10
NETRC_LOC = '~/.netrc'  # location of .netrc
WHITESPACES = '\n\t\r '

class Lexer:
    def __init__(self, fp) -> None:
        self.fp = fp  # _io.TextIOWrapper
        self.line = 1
        self.priority_stack = []

    def next_char(self):
        char = self.fp.read(1)
        if char == '\n':
            self.line += 1
        return char
    
    def fetch_token(self):
        if self.priority_stack:
            return self.priority_stack.pop()
        
        tok = ''
        file_iterator = iter(self.next_char, sentinel='')
        for character in file_iterator:
            if character in WHITESPACES:
                continue  # Skip

            if character in '"':
                tok = self.append_to_token(file_iterator, tok)
            else:
                if character == '\\':  # We have an escape sequence
                    character = self.next_char()

                tok += character
                tok = self.append_to_token(file_iterator, tok)

            return tok
                    

    def push_priority_stack(self, value):
        self.priority_stack.append(value)

    def append_to_token(self, file_iterator: iter, tok: str) -> str:
        for character in file_iterator:
            if character == '"':  # The double quotes instantly end
                return tok
            elif character == '\\':  # We have an escape sequence
                character = self.next_char()

            tok += character  # Puts the character, next character if we're in an escape sequence (Eg. \n)

        return tok

def get_auth(url: str):
    loc = os.path.expanduser(NETRC_LOC)
    if not os.path.exists(loc): return

    parse_res = urlparse(url)
    split = b':'
    host = parse_res.netloc.split(split)[0]

    hosts = {}

    with open(os.path.expanduser(NETRC_LOC), encoding='utf-8') as fp:
        """
        Example contents of .netrc:
            machine host1.austin.century.com login fred password bluebonnet
        """
        lexer = Lexer(fp)
        while True:
            line_number: int = lexer.line
            tok = lexer.fetch_token()

            if not tok:  # Basically, tok == '', which we only get at the sentinel (end)
                break
            elif tok[0] == '#':
                if lexer.line == line_number and len(tok) == 1:  # We got a hashtag character (comment)
                    lexer.fp.readline()  # Skip the line
                continue  # Next iteration
            elif tok == 'machine':
                entry = lexer.fetch_token()  # Next token
            elif tok == 'default':
                entry = 'default'
            else:
                raise LookupError("Invalid file contents")
            
            if not entry:
                raise LookupError("Invalid file contents")

            login = acc = password = ''
            hosts[entry] = {}
            while True:
                prev_line_number: int = lexer.line
                tok = lexer.fetch_token()
                if tok.startswith('#'):
                    if lexer.line == prev_line_number:
                        lexer.fp.readline()
                    continue
                if tok in {'', 'machine', 'default'}:
                    hosts[entry] = (login, acc, password)
                    lexer.push_priority_stack(tok)
                    break
                elif tok in ('login', 'user'):
                    login = lexer.fetch_token()
                elif tok == 'account':
                    acc = lexer.fetch_token()
                elif tok == 'password':
                    password = lexer.fetch_token()

    if host in hosts:
        ret = hosts[host]
    elif 'default' in hosts:
        ret = hosts['default']
    else:
        ret = None

    if ret:
        login = int(not ret[0])
        return ret[login], ret[2]
    else:
        raise ValueError("ret not processed")

def decode(text):
    return text if isinstance(text, str) else text.decode("ascii")

def select_proxy(url):
    proxies = {}
    parts = urlparse(url)
    if parts.hostname is None:
        return proxies.get(parts.scheme, proxies.get("all"))

    proxy_keys = [
        parts.scheme + "://" + parts.hostname,
        parts.scheme,
        "all://" + parts.hostname,
        "all",
    ]
    proxy = None
    for proxy_key in proxy_keys:
        if proxy_key in proxies:
            proxy = proxies[proxy_key]
            break

    return proxy

def add_scheme_if_needed(url, new):
        parsed = parse_url(url)
        scheme, auth, _, _, path, query, fragment = parsed

        netloc = parsed.netloc
        if not netloc:
            netloc, path = path, netloc

        if auth:
            netloc = "@".join([auth, netloc])
        if scheme is None:
            scheme = new
        if path is None:
            path = ""

        return urlunparse((scheme, netloc, path, "", query, fragment))

def proxy_headers(proxy):
    headers = {}
    auth = urlparse(proxy)
    user, passw = unquote(auth.username), unquote(auth.password)

    if user:
        headers['proxy-authorization'] = "Basic " + decode(b64encode(b':'.join((user, passw))).strip())

    return headers

class Adapter:
    def __init__(self) -> None:
        self.proxy_manager = {}

    def send(self, request):
        conn = self.fetch_conn(request.url)

    def fetch_conn(self, url):
        proxy = select_proxy(url)
        if proxy:
            proxy = add_scheme_if_needed(proxy, 'http')
            url = parse_url(proxy)
            manager = self.manager_for(proxy)
            conn = manager.connection_from_url(url)
        else:
            # TODO
            ...

    def manager_for(self, proxy):
        if proxy in self.proxy_manager:
            return self.proxy_manager[proxy]
        
        headers = proxy_headers(proxy)
        manager = self.proxy_manager[proxy] = proxy_from_url(
            proxy,
            proxy_headers=headers
        )
        return manager

class Request:
    def __init__(self, url: str, headers: dict[str, str]) -> None:
        self.url = url
        self.headers = headers

class RequestPrep:
    def __init__(self, url: str, headers: dict[str, str], auth, hooks: dict):
        self.url = url
        self.headers = headers
        self.auth = auth
        self.hooks = hooks

        self.adapters = {}
        self.add_adapter('http://', Adapter())
        self.add_adapter('https://', Adapter())

    def add_adapter(self, prefix, adapter):
        self.adapters[prefix] = adapter

class Session:
    def __init__(self) -> None:
        self.headers = DEFAULT_HEADERS
        self.hooks = DEFAULT_HOOKS
        self.redirect_lim = REDIRECT_LIMIT

    def prepare(self, req: Request):
        auth = get_auth(req.url)
        return RequestPrep().prepare(
            url=req.url,
            headers=self.headers | req.headers,
            auth=auth,
            hooks=self.hooks
        )

    def request(self, url: str):
        req = Request(url=url, headers=DEFAULT_HEADERS)

