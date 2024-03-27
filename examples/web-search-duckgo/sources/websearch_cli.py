'''
# dependency
pip install duckduckgo-search beautifulsoup4 requests selenium webdriver-manager

# on linux
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

def search_pubmed(query):
    site = "site:https://pubmed.ncbi.nlm.nih.gov"
    search_query = f"{query} {site}"
    results = DDGS().text(keywords=search_query, max_results=3)
    return results

def search_uptodate(query):
    site = "site:https://doctorabad.com/uptodate"
    search_query = f"{query} {site}"
    results = DDGS().text(keywords=search_query, max_results=3)
    return results

def url_to_filename(url):
    name = url.replace('https://', '').replace('/', '_').replace(':', '_').replace('?', '_')
    return f"{name}.txt"

def fetch_content_and_save(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text()
            filename = url_to_filename(url)
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"URL: {url}\n\nContent:\n{content}\n")
            print(f"Content saved to {filename}")
        else:
            print(f"Failed to retrieve {url}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def fetch_content_and_save_selenium(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        driver.get(url)
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "topicText")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#topicText")))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = soup.get_text()

        filename = url_to_filename(url)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"URL: {url}\n\nContent:\n{content}\n")
        print(f"Content saved to {filename}")

        driver.quit()
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Search PubMed and UpToDate using DuckDuckGo.')
    parser.add_argument('-t', '--type', choices=['pubmed', 'uptodate'], required=True, help='Type of search: pubmed or uptodate')
    parser.add_argument('-q', '--query', required=True, help='Search query')

    args = parser.parse_args()

    if args.type == 'pubmed':
        results = search_pubmed(args.query)
        for result in results:
            print(result)
        for result in results:
            fetch_content_and_save(result['href'])
    elif args.type == 'uptodate':
        results = search_uptodate(args.query)
        for result in results:
            print(result)
        for result in results:
            fetch_content_and_save_selenium(result['href'])

if __name__ == '__main__':
    main()
