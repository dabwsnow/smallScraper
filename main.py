import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "https://books.toscrape.com/"

class BookScraper:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def _parse(self, url):
        response = self.session.get(url)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')

    def categories(self):
        soup = self._parse(self.base_url)
        items = soup.select('.side_categories ul.nav-list > li > ul > li > a')
        return [
            {
                "name": item.text.strip(),
                "link": urljoin(self.base_url, item['href'])
            }
            for item in items
        ]

    def scrape_page(self, url, offset=1):
        soup = self._parse(url)
        cards = soup.find_all('article', class_='product_pod')
        items = []

        for idx, card in enumerate(cards, start=offset):
            items.append({
                "position": idx,
                "title": card.h3.a['title'],
                "image": urljoin(url, card.find('img')['src']),
                "link": urljoin(url, card.h3.a['href']),
                "rating": card.find('p', class_='star-rating')['class'][1],
                "price": card.find('p', class_='price_color').text,
                "stock": card.find('p', class_='instock availability').text.strip()
            })

        next_page = soup.select_one('li.next a')
        next_url = urljoin(url, next_page['href']) if next_page else None
        return items, next_url

    def scrape(self, max_pages=None):
        results = []
        target = self.base_url
        index = 1
        page = 0

        while target:
            page += 1
            print(f"Page {page}: {target}")
            items, next_url = self.scrape_page(target, offset=index)
            results.extend(items)
            index += len(items)
            target = next_url
            if max_pages and page >= max_pages:
                break

        return results

if __name__ == "__main__":
    client = BookScraper()

    categories = client.categories()
    print(f"Categories: {len(categories)}")

    books = client.scrape()
    print(f"Books: {len(books)}")

    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
