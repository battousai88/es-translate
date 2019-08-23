import io
import json
import requests

CONFIG_FILEPATH = '/Users/buddy/code/python/dictionary-scraper/config.json'


class HttpHelper(object):
    def __init__(self, base_url, user_agent, host, referer):
        self.base_url = base_url
        self.user_agent = user_agent
        self.host = host
        self.referer = referer
        self.cookie = ''

    def get(self, url):
        if not self.cookie:
            self.reload_cookie()
        return self.__create_http_request(url)

    def get_download(self, url):
        if not self.cookie:
            self.reload_cookie()
        return self.__create_download_http_request(url)

    def __create_http_request(self, url):
        headers = {
            'user-agent': self.user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self.cookie,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers'
        }

        return requests.get(url, headers=headers)

    def reload_cookie(self):
        with io.open(CONFIG_FILEPATH) as f:
            config = json.load(f)
            self.cookie = config['cookie']
