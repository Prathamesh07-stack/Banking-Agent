import requests
from tools.playwright_fetcher import (
    PlaywrightFetcher
)


class WebCrawler:

    def __init__(self):

        self.playwright = (
            PlaywrightFetcher()
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        self.blocked_patterns = [
            "Cloudflare",
            "Error 1000",
            "DNS points to prohibited IP",
            "Access Denied",
            "Attention Required",
            "403 Forbidden",
            "Forbidden",
            "Request blocked",
            "Access restricted",
            "Bot detected"
        ]

    def _is_blocked_page(
        self,
        html: str
    ) -> bool:

        if not html:
            return True

        html_lower = html.lower()

        for pattern in self.blocked_patterns:

            if pattern.lower() in html_lower:
                return True

        return False

    def fetch_page(
        self,
        url: str
    ) -> str:

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=20
            )

            response.raise_for_status()

            html = response.text

            if not self._is_blocked_page(
                html
            ):
                return html

            print(
                f"[BLOCKED] Requests blocked: {url}"
            )

            with open(
                "blocked_requests.html",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html)

        except Exception as e:

            print(
                f"[REQUESTS FAILED] {url}"
            )

            print(e)

        print(
            "[FALLBACK] Using Playwright"
        )

        html = (
            self.playwright.fetch_page(
                url
            )
        )

        if self._is_blocked_page(
            html
        ):

            print(
                f"[BLOCKED] Playwright blocked: {url}"
            )

            with open(
                "blocked_playwright.html",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html)

            return ""

        return html