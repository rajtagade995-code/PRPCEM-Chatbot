"""
PRPCEM College Assistant - URL Manager
Handles URL normalization, domain validation, depth tracking, and deduplication.
"""

from urllib.parse import urlparse, urljoin, urldefrag
import re
import config

class URLManager:
    def __init__(self, allowed_domains=None):
        self.allowed_domains = allowed_domains or config.ALLOWED_DOMAINS
        self.visited_urls = set()

    def normalize_url(self, raw_url, base_url=None):
        """Normalizes and resolves relative URLs into an absolute, clean form."""
        if not raw_url:
            return None

        # Clean string
        raw_url = raw_url.strip()
        if raw_url.startswith(("javascript:", "mailto:", "tel:", "#")):
            return None

        # Resolve relative links
        if base_url:
            raw_url = urljoin(base_url, raw_url)

        # Remove fragment (#section)
        clean_url, _ = urldefrag(raw_url)

        try:
            parsed = urlparse(clean_url)
        except Exception:
            return None

        # Must have http or https
        if parsed.scheme not in ("http", "https"):
            return None

        hostname = parsed.netloc.lower()
        # Strip port if standard
        if ":" in hostname:
            host_part, port_part = hostname.split(":", 1)
            if (parsed.scheme == "http" and port_part == "80") or (parsed.scheme == "https" and port_part == "443"):
                hostname = host_part

        # Normalize path
        path = parsed.path or "/"
        # Eliminate double slashes
        path = re.sub(r"/+", "/", path)

        # Build normalized URL
        normalized = f"{parsed.scheme}://{hostname}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"

        return normalized

    def is_allowed_domain(self, url):
        """Verifies if the URL domain is in the approved whitelist."""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower()
            if ":" in hostname:
                hostname = hostname.split(":")[0]

            for allowed in self.allowed_domains:
                if hostname == allowed or hostname.endswith("." + allowed):
                    return True
            return False
        except Exception:
            return False

    def is_pdf(self, url):
        """Checks if the URL points to a PDF document."""
        if not url:
            return False
        clean = url.lower().split("?")[0]
        return clean.endswith(".pdf")

    def mark_visited(self, url):
        self.visited_urls.add(url)

    def is_visited(self, url):
        return url in self.visited_urls

    def reset(self):
        self.visited_urls.clear()
