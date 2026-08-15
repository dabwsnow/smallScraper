import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

class BookScraper:
    def __init__(self, base_url="https://books.toscrape.com/"):
        self.base_url = base_url
        self.session = requests.Session()

    def _get_soup(self, url):
        response = self.session.get(url)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')

    def get_categories(self):
        soup = self._get_soup(self.base_url)
        cat_links = soup.select('.side_categories ul.nav-list > li > ul > li > a')
        categories = []
        for cat in cat_links:
            categories.append({
                "name": cat.text.strip(),
                "link": urljoin(self.base_url, cat['href'])
            })
        return categories

    def get_books_from_page(self, url, start_position=1):
        soup = self._get_soup(url)
        book_elements = soup.find_all('article', class_='product_pod')
        books = []
        for idx, book in enumerate(book_elements, start=start_position):
            title = book.h3.a['title']
            link = urljoin(url, book.h3.a['href'])
            image = urljoin(url, book.find('img')['src'])
            rating = book.find('p', class_='star-rating')['class'][1]
            price = book.find('p', class_='price_color').text
            stock = book.find('p', class_='instock availability').text.strip()

            books.append({
                "position": idx,
                "title": title,
                "image": image,
                "link": link,
                "rating": rating,
                "price": price,
                "stock": stock
            })

        next_btn = soup.select_one('li.next a')
        next_url = urljoin(url, next_btn['href']) if next_btn else None
        return books, next_url

    def get_all_books(self, max_pages=None):
        all_books = []
        current_url = self.base_url
        position = 1
        page_count = 0

        while current_url:
            page_count += 1
            print(f"Scraping page {page_count}: {current_url}")
            books, next_url = self.get_books_from_page(current_url, start_position=position)
            all_books.extend(books)
            position += len(books)
            current_url = next_url
            if max_pages and page_count >= max_pages:
                break

        return all_books

if __name__ == "__main__":
    scraper = BookScraper()

    print("Fetching categories...")
    categories = scraper.get_categories()
    print(f"Found {len(categories)} categories.")

    print("Scraping all books (pagination)...")
    all_books = scraper.get_all_books()
    print(f"Total books scraped: {len(all_books)}")

    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)
