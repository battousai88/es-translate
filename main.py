import os
import argparse
import time
import urllib3
from logger import Logger
from pathlib import Path
from http_helper import HttpHelper
from html_parser import DictHtmlParser

BASE_URL = 'https://www.spanishdict.com'
HOST = urllib3.get_host(BASE_URL)[1]
SEARCH_URL = '{0}/translate/'.format(BASE_URL)
CONJUGATE_URL = '{0}/conjugate'.format(BASE_URL)
PROJECT_FILEPATH = os.getcwd()
DOWNLOAD_FILEPATH = '{0}/downloads'.format(PROJECT_FILEPATH)
JSON_DOWNLOAD_FILEPATH = '{0}/json'.format(DOWNLOAD_FILEPATH)
HTML_TRANSLATION_DOWNLOAD_FILEPATH = '{0}/translate'.format(DOWNLOAD_FILEPATH)
HTML_CONJUGATION_DOWNLOAD_FILEPATH = '{0}/conjugate'.format(DOWNLOAD_FILEPATH)
LOG_FILEPATH = "{0}/logs".format(PROJECT_FILEPATH)
JSON_HISTORY_LOG = '{0}/.json_history'.format(LOG_FILEPATH)
HTML_HISTORY_LOG = '{0}/.history'.format(LOG_FILEPATH)
ERROR_LOG = '{0}/.error_log'.format(LOG_FILEPATH)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scrape', help='Scrape words')
    parser.add_argument(
        '-p', '--parse', help='Parse dictionary entries from downloaded html pages')
    parser.add_argument('-d', '--define', help='Define word')
    parser.add_argument('-i', '--input', help='Input file containing list of words to define/conjugate.')
    return parser


def parse_args():
    parser = create_parser()
    args = parser.parse_args()
    return args


def create_search_url(keyword):
    return SEARCH_URL.format(keyword)


def get_log(filename):
    return Logger(filename)


def save_file(filename, data):
    try:
        with open(filename, 'w+') as f:
            f.write(data)
    except IOError as e:
        print('Error saving file: {0}'.format(e.message))


def parse_html(html):
    dict_parser = DictHtmlParser()
    return dict_parser.parse_html(html)


def parse_html_pages(dir, save_to_json):
    json_log = get_log(JSON_HISTORY_LOG)
    error_log = get_log(ERROR_LOG)

    try:
        words = []
        dict_parser = DictHtmlParser()
        p = Path(dir)
        files = [x for x in p.iterdir()]
        for file in files:
            name = os.path.splitext(os.path.basename(file))[0]
            if name not in json_log.items:
                print('Parsing {0}...'.format(file))
                with open(file, encoding='utf-8') as f:
                    try:
                        word = parse_html(f.read())
                        if save_to_json:
                            print('Saving {0}.json'.format(word.text))
                            filename = '{0}/{1}.json'.format(
                                JSON_DOWNLOAD_FILEPATH, word.text)
                            save_file(filename, word.toJSON())
                            json_log.append(word.text)
                    except Exception e:
                        print('Error parsing {0}:{1}'.format(name, e.message))
                        error_log.append(name)
    except IOError as e:
        print('Error parsing html: {0}'.format(e.message))


def load_common_words():
    try:
        words = []
        with open("{0}".format(words_filepath), 'r') as f:
            words = f.read().splitlines()
        return words
    except IOError as e:
        print('Error: {0}'.format(e.message))


def read_downloaded_html(word):
    try:
        with open("{0}/{1}.html".format(DOWNLOAD_FILEPATH, word), encoding='utf-8') as f:
            html = f.read()
            return html
    except IOError as e:
        print('Error: {0}'.format(e.message))


def define(word):
    html = read_downloaded_html(word)
    word = parse_html(html)
    print(word.quick_translations)


def conjugate(word):
    html = read_downloaded_html(word)
    conjugated = parse_html(html)


def scrape(logfile):
    common_words = load_common_words()
    referer = BASE_URL
    http_req = HttpHelper(BASE_URL, MAC_USER_AGENT, HOST, BASE_URL)
    print('Running...')
    for word in common_words:
        if word not in logfile.items:
            res = http_req.get(create_search_url(word))
            fname = "{0}/{1}.html".format(HTML_TRANSLATION_DOWNLOAD_FILEPATH, word)
            save_file(fname, res.text)
            logfile.append(word)
            time.sleep(2)
    print('Done!')


if __name__ == '__main__':
    parser = create_parser()
    args = parse_args()
    words_filepath = ''

    if args.input:
        words_filepath = args.input
    if args.parse:
        parse_html_pages('{0}'.format(HTML_TRANSLATION_DOWNLOAD_FILEPATH), args.parse)
    if args.define:
        define(args.define)
    if args.scrape:
        history_log = get_log(HTML_HISTORY_LOG)
        scrape(history_log)
