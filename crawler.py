import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)

# Ministerul Mediului
base_url = "http://www.mmediu.ro/categorie/programul-anual-al-achizitiilor-publice/167"

visited = []

urls_to_visit = [base_url]


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
        # if url not in visited and url not in urls_to_visit and (".pdf" in url or ".xls" in url):
        #     urls_to_visit.append(url)
        if url not in visited and url not in urls_to_visit:
            urls_to_visit.append(url)


def run():
    while urls_to_visit:
        url = urls_to_visit.pop(0)
        logging.info(f'Crawling: {url}')

        try:
            crawl(url)
        except Exception as e:
            logging.exception(f'Failed to crawl {url}: {e}')
        finally:
            visited.append(url)


if __name__ == '__main__':
    run()