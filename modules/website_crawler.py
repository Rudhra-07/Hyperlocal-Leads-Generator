import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import logger
from urllib.parse import urljoin, urlparse

class WebsiteCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.contact_patterns = ['/contact', '/contact-us', '/about', '/find-us', '/get-in-touch', '/reach-us']

    def _get_selenium_driver(self):
        """Setup headless Selenium driver."""
        chrome_options = Options()
        if Config.SELENIUM_HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(Config.CRAWL_TIMEOUT)
        return driver

    def crawl(self, url: str) -> Dict[str, Any]:
        """Crawl homepage and contact pages for a website."""
        if not url:
            return {}

        logger.info(f"Crawling: {url}")
        
        results = {
            'homepage_text': "",
            'contact_page_text': "",
            'social_links': set(),
            'other_pages_content': []
        }

        try:
            # Step 1: Request Homepage (Requests/BS4)
            response = requests.get(url, headers=self.headers, timeout=Config.CRAWL_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            results['homepage_text'] = soup.get_text(separator=' ', strip=True)
            
            # Extract social links
            results['social_links'].update(self._extract_social_links(soup, url))
            
            # Step 2: Discover Contact Pages
            contact_urls = self._discover_contact_urls(soup, url)
            
            # Step 3: Crawl Contact Pages
            for c_url in contact_urls[:2]: # Crawl up to 2 contact pages
                try:
                    c_resp = requests.get(c_url, headers=self.headers, timeout=10)
                    c_resp.raise_for_status()
                    c_soup = BeautifulSoup(c_resp.text, 'lxml')
                    results['other_pages_content'].append(c_soup.get_text(separator=' ', strip=True))
                    results['social_links'].update(self._extract_social_links(c_soup, c_url))
                except Exception as e:
                    logger.warning(f"Failed to crawl contact page {c_url}: {e}")

            # Merge contact texts
            results['contact_page_text'] = " ".join(results['other_pages_content'])
            
            # Step 4: Fallback to Selenium if content is sparse
            if len(results['homepage_text']) < 500:
                logger.info(f"Low content found for {url}. Falling back to Selenium...")
                results.update(self._crawl_with_selenium(url))

            results['social_links'] = list(results['social_links'])
            return results

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {}

    def _discover_contact_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find potential contact pages."""
        found_urls = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Absolute URL check
            abs_url = urljoin(base_url, href)
            # Ensure it belongs to the same domain
            if urlparse(abs_url).netloc == urlparse(base_url).netloc:
                if any(pattern in abs_url.lower() for pattern in self.contact_patterns):
                    found_urls.append(abs_url)
        return list(set(found_urls))

    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract common social media links."""
        social_domains = ['facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com']
        social_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(domain in href.lower() for domain in social_domains):
                social_links.append(href)
        return social_links

    def _crawl_with_selenium(self, url: str) -> Dict[str, Any]:
        """Crawl website using Selenium for JS rendering."""
        driver = None
        try:
            driver = self._get_selenium_driver()
            driver.get(url)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            return {
                'homepage_text': soup.get_text(separator=' ', strip=True),
                'social_links': self._extract_social_links(soup, url)
            }
        except Exception as e:
            logger.error(f"Selenium crawling failed for {url}: {e}")
            return {}
        finally:
            if driver:
                driver.quit()
