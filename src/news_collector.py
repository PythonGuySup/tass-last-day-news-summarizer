import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import TASS_URL


class TASSNewsCollector:
    def __init__(self, base_url: str = TASS_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_news_links(self) -> List[str]:
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            links = []

            all_links = soup.find_all('a', href=re.compile(r'/.*\d+'))

            for link in all_links:
                href = link['href']
                if href and not href.startswith('http'):
                    full_url = self.base_url + href if href.startswith('/') else f"{self.base_url}/{href}"
                    if full_url not in links:
                        links.append(full_url)

                    if len(links) >= 15:
                        break

            return links

        except Exception as e:
            print(f"Ошибка при получении ссылок: {e}")
            return []

    def extract_article_content(self, url: str) -> Dict[str, str]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            title = "Без заголовка"
            title_elements = soup.find_all(['h1', 'h2', 'h3'])
            for element in title_elements:
                text = element.get_text().strip()
                if len(text) > 10 and len(text) < 200:
                    title = text
                    break

            content_parts = []

            content_selectors = [
                '.text-block',
                '.article-content',
                '.news-content',
                '.content',
                'article',
                '.text'
            ]

            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    text = ' '.join(text.split())
                    if len(text) > 100:
                        content_parts.append(text)

            if not content_parts:
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    text = ' '.join(text.split())
                    if len(text) > 50:
                        content_parts.append(text)

            content = ' '.join(content_parts[:8])

            return {
                'title': title,
                'content': content,
                'url': url,
                'timestamp': datetime.now()
            }

        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
            return None

    def get_last_24h_news(self) -> List[Dict]:
        """Получает новости"""
        print("Сбор новостей с ТАСС...")
        links = self.get_news_links()
        articles = []

        print(f"Найдено {len(links)} ссылок. Обработка...")

        for i, link in enumerate(links, 1):
            print(f"Обработка статьи {i}/{len(links)}...")
            article = self.extract_article_content(link)
            if article and article['content'] and len(article['content']) > 20:
                articles.append(article)
                print(f"✓ Добавлена: {article['title'][:60]}...")
            else:
                print(f"✗ Пропущена (мало контента)")
            time.sleep(0.5)

        print(f"Успешно собрано {len(articles)} новостей")
        return articles
