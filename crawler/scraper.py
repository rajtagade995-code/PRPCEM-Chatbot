"""
PRPCEM College Assistant - Scraper
HTML parser with support for standard web pages, Angular SPA routing, and PDF discovery.
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import config
from crawler.url_manager import URLManager
from crawler.text_cleaner import TextCleaner

class Scraper:
    def __init__(self):
        self.url_manager = URLManager()
        self.headers = {"User-Agent": config.CRAWLER_USER_AGENT}

    def scrape_url(self, url):
        """Scrapes a URL, extracts metadata, headings, text content, links, and PDF references."""
        scraped_data = {
            "url": url,
            "title": "",
            "headings": [],
            "content": "",
            "links": [],
            "pdf_links": [],
            "category": "General",
            "status_code": 0,
            "error": None
        }

        try:
            response = requests.get(url, headers=self.headers, timeout=config.REQUEST_TIMEOUT)
            scraped_data["status_code"] = response.status_code
            if response.status_code != 200:
                scraped_data["error"] = f"HTTP {response.status_code}"
                return scraped_data

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract Title
            if soup.title and soup.title.string:
                scraped_data["title"] = soup.title.string.strip()
            elif soup.find("h1"):
                scraped_data["title"] = soup.find("h1").get_text().strip()
            else:
                scraped_data["title"] = "PRPCEM College Page"

            # Extract Headings
            headings = []
            for h in soup.find_all(["h1", "h2", "h3", "h4"]):
                txt = h.get_text().strip()
                if txt and len(txt) > 2:
                    headings.append(txt)
            scraped_data["headings"] = headings

            # Extract paragraphs and readable body text
            body_text = TextCleaner.clean_html(str(soup.body if soup.body else soup))
            
            # Extract Structured Tables (Requirement #15)
            table_text = self._extract_structured_tables(soup)
            if table_text:
                body_text += "\n\n" + table_text

            scraped_data["content"] = body_text

            # Extract Links
            raw_links = []
            pdf_links = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                normalized = self.url_manager.normalize_url(href, base_url=url)
                if not normalized:
                    continue

                if self.url_manager.is_pdf(normalized):
                    pdf_links.append(normalized)
                elif self.url_manager.is_allowed_domain(normalized):
                    raw_links.append(normalized)

            # Special PRPCEM Angular SPA Discovery:
            # If the page includes main.*.js, inspect it for internal routes and PDFs
            scripts = soup.find_all("script", src=True)
            for script in scripts:
                src = script["src"]
                if "main." in src and src.endswith(".js"):
                    bundle_url = urljoin(url, src)
                    spa_routes, spa_pdfs = self._inspect_angular_bundle(bundle_url)
                    raw_links.extend(spa_routes)
                    pdf_links.extend(spa_pdfs)

            scraped_data["links"] = list(set(raw_links))
            scraped_data["pdf_links"] = list(set(pdf_links))
            scraped_data["category"] = TextCleaner.categorize_text(body_text, url)

            return scraped_data

        except Exception as e:
            scraped_data["error"] = str(e)
            return scraped_data

    def _inspect_angular_bundle(self, bundle_url):
        """Discovers Angular SPA client-side routes and PDF document links from bundle."""
        discovered_routes = []
        discovered_pdfs = []
        try:
            res = requests.get(bundle_url, headers=self.headers, timeout=config.REQUEST_TIMEOUT)
            if res.status_code == 200:
                text = res.text
                # Extract Angular path routes
                routes = re.findall(r'path:\s*["\']([a-zA-Z0-9_\-\/]+)["\']', text)
                for r in routes:
                    # Ignore template expressions
                    if "{" in r or "}" in r:
                        continue
                    full_url = urljoin(config.COLLEGE_WEBSITE, r)
                    if self.url_manager.is_allowed_domain(full_url):
                        discovered_routes.append(full_url)

                # Extract PDF URLs in bundle
                pdfs = re.findall(r'https?://[^\s"\'<>]+\.pdf', text, re.IGNORECASE)
                for p in pdfs:
                    if self.url_manager.is_allowed_domain(p):
                        discovered_pdfs.append(p)
        except Exception:
            pass

        return discovered_routes, discovered_pdfs

    def _extract_structured_tables(self, soup):
        """Extracts HTML tables as structured key-value/row text."""
        table_texts = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [c.get_text(separator=" ").strip() for c in tr.find_all(["th", "td"])]
                clean_cells = [re.sub(r"\s+", " ", cell) for cell in cells if cell]
                if clean_cells:
                    rows.append(" | ".join(clean_cells))
            if rows:
                table_texts.append("\n[STRUCTURED TABLE]:\n" + "\n".join(rows))
        return "\n\n".join(table_texts)
