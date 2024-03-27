'''
# dependency
pip install duckduckgo-search beautifulsoup4 requests selenium webdriver-manager

# install on linux
apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome*.deb
'''

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

class WebAcadSearch:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    def search(self, query, site):
        search_query = f"{query} site:{site}"
        results = DDGS().text(keywords=search_query, max_results=3)
        return results

    def url_to_filename(self, url):
        name = url.replace('https://', '').replace('/', '_').replace(':', '_').replace('?', '_')
        return f"{name}.txt"

    def fetch_content_and_save(self, url, search_pattern, is_pubmed=False):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, search_pattern)))
                if is_pubmed:
                    abstract_div = driver.find_element(By.CSS_SELECTOR, "div.abstract-content.selected#eng-abstract")
                    content = abstract_div.text.strip()
                else:
                    content = driver.find_element(By.CSS_SELECTOR, search_pattern).text.strip()

                filename = self.url_to_filename(url)
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(f"URL: {url}\n\nContent:\n{content}\n")
                print(f"Content saved to {filename}")
            except (WebDriverException, NoSuchElementException) as e:
                print(f"Skipping {url} due to exception: {str(e)}")

            driver.quit()
        except Exception as e:
            print(f"Error fetching {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Search PubMed and UpToDate using DuckDuckGo.')
    parser.add_argument('-t', '--type', choices=['pubmed', 'uptodate'], required=True, help='Type of search: pubmed or uptodate')
    parser.add_argument('-q', '--query', required=True, help='Search query')

    args = parser.parse_args()

    web_acad_search = WebAcadSearch()

    if args.type == 'pubmed':
        results = web_acad_search.search(args.query, "https://pubmed.ncbi.nlm.nih.gov")
        for result in results:
            print(result)
            web_acad_search.fetch_content_and_save(result['href'], search_pattern=".abstract-content.selected#eng-abstract", is_pubmed=True)
    elif args.type == 'uptodate':
        results = web_acad_search.search(args.query, "https://doctorabad.com/uptodate")
        for result in results:
            print(result)
            web_acad_search.fetch_content_and_save(result['href'], search_pattern="div#topicText")

if __name__ == '__main__':
    main()
