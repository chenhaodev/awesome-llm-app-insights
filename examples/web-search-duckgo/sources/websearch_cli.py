import argparse
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import os
import logging

class WebAcadSearch:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        self.output_folder = "search_results"
        os.makedirs(self.output_folder, exist_ok=True)
        self.log_file = os.path.join(self.output_folder, "search_log.txt")
        self.logger = self.setup_logging()
        self.sources_config = {
            "pubmed": {
                "url": "https://pubmed.ncbi.nlm.nih.gov",
                "search_pattern": ".abstract-content.selected#eng-abstract"
            },
            "uptodate": {
                "url": "https://doctorabad.com/uptodate",
                "search_pattern": "div#topicText"
            },
            "semantic_scholar": {
                "url": "https://www.semanticscholar.org",
                "search_pattern": ".tldr-abstract-replacement.paper-detail-page__tldr-abstract"
            }
        }

    def setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def search(self, query, site):
        search_query = f"{query} site:{site}"
        results = DDGS().text(keywords=search_query, max_results=3)
        return results

    def url_to_filename(self, url):
        name = url.replace('https://', '').replace('/', '_').replace(':', '_').replace('?', '_')
        return f"{name}.txt"

    def fetch_content_and_save(self, url, search_pattern):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, search_pattern)))
                abstract_div = driver.find_element(By.CSS_SELECTOR, search_pattern)
                content = abstract_div.text.strip()

                filename = self.url_to_filename(url)
                filepath = os.path.join(self.output_folder, filename)
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(f"URL: {url}\n\nContent:\n{content}\n")
                self.logger.info(f"Content saved to {filepath}")
            except (WebDriverException, NoSuchElementException) as e:
                self.logger.warning(f"Skipping {url} due to exception: {str(e)}")

            driver.quit()
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")

    def perform_search(self, search_type, query):
        if search_type in self.sources_config:
            config = self.sources_config[search_type]
            results = self.search(query, config["url"])
            self.logger.info(f"{search_type.capitalize()} Results:")
            for result in results:
                self.logger.info(result)
                self.fetch_content_and_save(result['href'], search_pattern=config["search_pattern"])
        elif search_type == 'all':
            for source, config in self.sources_config.items():
                results = self.search(query, config["url"])
                self.logger.info(f"{source.capitalize()} Results:")
                for result in results:
                    self.logger.info(result)
                    self.fetch_content_and_save(result['href'], search_pattern=config["search_pattern"])

def main():
    parser = argparse.ArgumentParser(description='Search PubMed, UpToDate, and Semantic Scholar using DuckDuckGo.')
    parser.add_argument('-t', '--type', choices=['pubmed', 'uptodate', 'semantic_scholar', 'all'], required=True, help='Type of search: pubmed, uptodate, semantic_scholar, or all')
    parser.add_argument('-q', '--query', required=True, help='Search query')

    args = parser.parse_args()

    web_acad_search = WebAcadSearch()
    web_acad_search.perform_search(args.type, args.query)

if __name__ == '__main__':
    main()