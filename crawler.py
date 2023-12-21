import requests
import logging
import os
import re

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)

PAPs_PATTERN = r'(paap|\s*achizitii\s*publice)'

base_url_1 = "https://www.mcid.gov.ro/interes-public/achizitii-publice/"
base_url_2 = "https://ms.ro/informatii-de-interes-public/achizitii-publice/"
base_url_3 = "http://www.mmediu.ro/categorie/programul-anual-al-achizitiilor-publice/167"

visited = []

urls_to_visit = [base_url_1, base_url_2, base_url_3]


def get_linked_url(url, html):
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('a'):
        path = link.get('href')

        if path and path.startswith('/'):
            path = urljoin(url, path)

        yield path


def crawl(url):
    html = requests.get(url).text

    for url in get_linked_url(url, html):
        if ".pdf" in url or ".xls" in url:
            download_file(url)


def download_file(url):
    response = requests.get(url)
    filename = url.rpartition('/')[-1]
    logging.info(f'Found file: {filename}')

    if (is_pap_file(filename)):
        with open(filename, 'wb') as f:
            f.write(response.content)
            f.close
            logging.info('Download completed!')


def is_pap_file(filename):
    pattern = re.compile(PAPs_PATTERN, re.IGNORECASE)
    return bool(pattern.search(filename))

def setup_dir(url):
    base_dir = os.getcwd()
    dir_name = urlparse(url).netloc

    logging.info(f'Creating directory {dir_name}')
    os.mkdir(base_dir + '/' + dir_name)
    os.chdir(f'./{dir_name}')


def run():
    while urls_to_visit:
        url = urls_to_visit.pop(0)

        setup_dir(url)

        logging.info(f'Crawling: {url}')

        try:
            crawl(url)
        except Exception as e:
            logging.exception(f'Failed to crawl {url}: {e}')
        finally:
            visited.append(url)

        os.chdir('../')

if __name__ == '__main__':
    run()
