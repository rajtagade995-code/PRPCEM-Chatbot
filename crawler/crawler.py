"""
PRPCEM College Assistant - Web Crawler
Asynchronous / threaded crawler with BFS queue, depth control, PDF extraction,
content-hash change detection, and live status reporting.
"""

import threading
import time
import json
import os
from collections import deque
from datetime import datetime
import config
from crawler.url_manager import URLManager
from crawler.scraper import Scraper
from crawler.pdf_parser import PDFParser
from crawler.text_cleaner import TextCleaner
from crawler.knowledge_extractor import KnowledgeExtractor
from database.database import get_db_connection, set_setting, generate_coverage_report

class Crawler:
    def __init__(self):
        self.url_manager = URLManager()
        self.scraper = Scraper()
        self.pdf_parser = PDFParser()
        self.knowledge_extractor = KnowledgeExtractor()
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()

        # Status tracking
        self.status = {
            "state": "idle",             # idle, crawling, completed, stopped, error
            "message": "Ready to crawl",
            "pages_scanned": 0,
            "pages_stored": 0,
            "pdfs_found": 0,
            "errors": 0,
            "current_url": "",
            "start_time": None,
            "finish_time": None
        }

    def get_status(self):
        with self.lock:
            return dict(self.status)

    def start_crawl(self, max_pages=None, max_depth=None, update_mode=False):
        """Starts crawling in a background thread."""
        with self.lock:
            if self.is_running:
                return False, "Crawler is already running."
            self.is_running = True
            self.status["state"] = "crawling"
            self.status["message"] = "Crawling started..."
            self.status["pages_scanned"] = 0
            self.status["pages_stored"] = 0
            self.status["pdfs_found"] = 0
            self.status["errors"] = 0
            self.status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status["finish_time"] = None

        self.thread = threading.Thread(
            target=self._run_crawler,
            args=(max_pages or config.MAX_PAGES, max_depth or config.MAX_DEPTH, update_mode),
            daemon=True
        )
        self.thread.start()
        return True, "Crawler started successfully."

    def stop_crawl(self):
        with self.lock:
            if not self.is_running:
                return False, "Crawler is not running."
            self.is_running = False
            self.status["state"] = "stopped"
            self.status["message"] = "Crawling stopped by administrator."
        return True, "Stopping crawler..."

    def _run_crawler(self, max_pages, max_depth, update_mode):
        """Internal crawl execution using breadth-first search."""
        start_urls = [
            config.COLLEGE_WEBSITE,
            getattr(config, "COLLEGE_ACADEMICS_WEBSITE", "https://academics.prpotepatilengg.ac.in/"),
            getattr(config, "COLLEGE_EXAMCELL_WEBSITE", "https://examcell.prpotepatilengg.ac.in/")
        ]
        queue = deque([(u, 0) for u in start_urls])
        self.url_manager.reset()
        for u in start_urls:
            self.url_manager.mark_visited(u)

        conn = get_db_connection()
        pdf_urls_seen = set()
        crawled_summary = []

        try:
            while queue and self.is_running:
                if self.status["pages_scanned"] >= max_pages:
                    break

                current_url, depth = queue.popleft()

                with self.lock:
                    self.status["current_url"] = current_url
                    self.status["pages_scanned"] += 1
                    self.status["message"] = (
                        f"Crawling... Pages scanned: {self.status['pages_scanned']}, "
                        f"Pages stored: {self.status['pages_stored']}, "
                        f"PDFs found: {self.status['pdfs_found']}, "
                        f"Errors: {self.status['errors']}"
                    )

                # Scrape HTML page
                scraped = self.scraper.scrape_url(current_url)

                if scraped["error"]:
                    with self.lock:
                        self.status["errors"] += 1
                    continue

                content = scraped["content"]
                content_hash = TextCleaner.compute_hash(content)

                # Check if page already exists
                existing = conn.execute(
                    "SELECT content_hash FROM pages WHERE url = ?", (current_url,)
                ).fetchone()

                should_store = False
                if not existing:
                    should_store = True
                elif update_mode and existing["content_hash"] != content_hash:
                    should_store = True

                if should_store and len(content) > 10:
                    conn.execute(
                        """INSERT INTO pages (url, title, content, category, content_hash, last_crawled)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ON CONFLICT(url) DO UPDATE SET
                               title = excluded.title,
                               content = excluded.content,
                               category = excluded.category,
                               content_hash = excluded.content_hash,
                               last_crawled = excluded.last_crawled""",
                        (
                            current_url,
                            scraped["title"],
                            content,
                            scraped["category"],
                            content_hash,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    )
                    conn.commit()
                    n = self.knowledge_extractor.extract_structured_facts(
                        url=current_url,
                        title=scraped["title"],
                        content=content,
                        category=scraped["category"]
                    )
                    with self.lock:
                        self.status["pages_stored"] += 1
                        self.status["records_created"] = self.status.get("records_created", 0) + n

                crawled_summary.append({
                    "url": current_url,
                    "title": scraped["title"],
                    "category": scraped["category"],
                    "depth": depth
                })

                # Process newly discovered PDFs (up to 5 per page step)
                pdf_batch_count = 0
                for pdf_url in scraped["pdf_links"]:
                    if not self.is_running:
                        break
                    if pdf_url not in pdf_urls_seen:
                        pdf_urls_seen.add(pdf_url)
                        pdf_batch_count += 1
                        with self.lock:
                            self.status["pdfs_found"] += 1

                        # Extract PDF content
                        pdf_data = self.pdf_parser.extract_text_from_url(pdf_url)
                        conn.execute(
                            """INSERT INTO documents (url, title, content, category, last_crawled)
                               VALUES (?, ?, ?, ?, ?)
                               ON CONFLICT(url) DO UPDATE SET
                                   title = excluded.title,
                                   content = excluded.content,
                                   category = excluded.category,
                                   last_crawled = excluded.last_crawled""",
                            (
                                pdf_url,
                                pdf_data["title"],
                                pdf_data["content"],
                                pdf_data["category"],
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                        )
                        conn.commit()
                        n_doc = self.knowledge_extractor.extract_structured_facts(
                            url=pdf_url,
                            title=pdf_data["title"],
                            content=pdf_data["content"],
                            category=pdf_data["category"]
                        )
                        with self.lock:
                            self.status["records_created"] = self.status.get("records_created", 0) + n_doc

                        if pdf_batch_count >= 5:
                            break

                # Queue next level links
                if depth < max_depth:
                    for link in scraped["links"]:
                        if not self.url_manager.is_visited(link):
                            self.url_manager.mark_visited(link)
                            queue.append((link, depth + 1))

                # Polite crawling delay
                time.sleep(0.2)

            with self.lock:
                self.is_running = False
                self.status["state"] = "completed"
                self.status["finish_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.status["message"] = (
                    f"Crawling completed. Pages scanned: {self.status['pages_scanned']}, "
                    f"Pages stored: {self.status['pages_stored']}, "
                    f"PDFs found: {self.status['pdfs_found']}, "
                    f"Records created: {self.status.get('records_created', 0)}, "
                    f"Errors: {self.status['errors']}"
                )

            # Update settings
            set_setting("last_crawl_time", self.status["finish_time"])
            set_setting("total_pages_crawled", self.status["pages_stored"])
            set_setting("total_pdfs_found", self.status["pdfs_found"])

            # Export data/crawled_pages.json
            os.makedirs(config.DATA_DIR, exist_ok=True)
            with open(config.CRAWLED_PAGES_JSON, "w", encoding="utf-8") as f:
                json.dump(crawled_summary, f, indent=2)

        except Exception as e:
            with self.lock:
                self.is_running = False
                self.status["state"] = "error"
                self.status["message"] = f"Error during crawl: {str(e)}"
        finally:
            conn.close()
            try:
                generate_coverage_report()
            except Exception:
                pass

# Singleton crawler instance
crawler_instance = Crawler()
