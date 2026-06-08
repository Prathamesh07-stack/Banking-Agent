import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain_core.tools import tool
from tools.crawler import WebCrawler
from tools.parser import ContentParser
from tools.bank_link_ranker import BankLinkRanker


class GoogleSearchTool:

    def __init__(self):
        self.crawler = WebCrawler()
        self.parser = ContentParser()
        self.link_ranker = BankLinkRanker()
        self.known_banks = {
            "sbi": "https://sbi.bank.in",
            "state bank of india": "https://sbi.bank.in",
            "hdfc": "https://www.hdfcbank.com",
            "icici": "https://www.icicibank.com",
            "axis": "https://www.axisbank.com",
            "rbi": "https://rbi.org.in",
            "hsbc": "https://www.hsbc.com"
        }

    def _extract_bank_name(
        self,
        query: str
    ) -> str:
        stop_words = {
            "current",
            "latest",
            "interest",
            "rate",
            "rates",
            "fd",
            "fixed",
            "deposit",
            "loan",
            "loans",
            "home",
            "personal",
            "car",
            "credit",
            "card",
            "repo"
        }

        words = []

        for word in query.lower().split():
            if word not in stop_words:
                words.append(word)
        return " ".join(words)

    def _find_bank_website(
        self,
        query: str
    ) -> str | None:
        query_lower = query.lower()

        for bank, website in self.known_banks.items():
            if bank in query_lower:
                return website

        bank_name = self._extract_bank_name(query)

        if not bank_name:
            return None

        print(
            f"[BANK SEARCH] Extracted Bank: "
            f"{bank_name}"
        )
        tokens = bank_name.split()
        joined = "".join(tokens)

        candidates = [
            f"https://www.{joined}.com",
            f"https://www.{joined}bank.com",
            f"https://www.{joined}.co.in",
            f"https://{joined}.com",
            f"https://{joined}.co.in",
            f"https://www.{joined}bank.in",
            f"https://www.{joined}.in",
            f"https://www.{joined}bank.org",
            f"https://www.{joined}.org",
        ]

        headers = { "User-Agent": "Mozilla/5.0"}

        for candidate in candidates:
            try:
                print(
                    f"[BANK SEARCH] Trying: "
                    f"{candidate}"
                )
                response = requests.get(
                    candidate,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )

                if response.status_code >= 400:
                    continue

                html = response.text.lower()
                matched_words = 0

                for token in tokens:
                    if token in html:
                        matched_words += 1

                if matched_words > 0:
                    print(
                        f"[BANK SEARCH] Found website: "
                        f"{response.url}"
                    )
                    return response.url
            except Exception:
                pass

        return None

    def _extract_internal_links(
        self,
        html: str,
        base_url: str
    ) -> list[dict]:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        links = []
        seen = set()

        for tag in soup.find_all(
            "a",
            href=True
        ):
            href = tag["href"]

            full_url = urljoin( base_url,href)
            if full_url in seen:
                continue

            if not full_url.startswith(base_url):
                continue

            seen.add(full_url)

            links.append(
                {
                    "url": full_url,
                    "text": tag.get_text(
                        " ",
                        strip=True
                    )
                }
            )
        return links

    def search(
        self,
        query: str
    ) -> str:

        try:
            print(f"\n[BANK SEARCH] Query: {query}")
            website = self._find_bank_website(
                query
            )

            if not website:
                return ("Unable to locate an official bank website.")

            print(f"[BANK SEARCH] Website: {website}")

            homepage_html = (
                self.crawler.fetch_page(
                    website
                )
            )
            if not homepage_html:
                return ("Unable to fetch bank website.")
            print(
                f"[DEBUG] Homepage Length: "
                f"{len(homepage_html)}"
            )
            with open(
                "homepage_debug.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write( homepage_html )

            links = (
                self._extract_internal_links(
                    homepage_html,
                    website
                )
            )

            print(f"[BANK SEARCH] Found {len(links)} links")

            relevant_links = (
                self.link_ranker.rank_links(
                    links,
                    query
                )
            )

            print("\n[BANK SEARCH] Selected Links:")

            for link in relevant_links:
                print(link)

            pages_to_crawl = [
                website
            ] + relevant_links[:3]

            contexts = []

            for page_url in pages_to_crawl:

                print(f"[CRAWLER] Fetching: {page_url}")

                html = (
                    self.crawler.fetch_page(
                        page_url
                    )
                )
                if not html:

                    contexts.append(
                        f"""
Source: {page_url}

Content could not be retrieved.

Possible reasons:
- Website protection
- Cloudflare blocking
- Access restrictions
- Request timeout
"""
                    )

                    continue

                text = (
                    self.parser.extract_text( html)
                )
                if not text:
                    contexts.append(
                        f"""
Source: {page_url}

Page retrieved but no readable content
was extracted.
"""
                    )

                    continue

                contexts.append(
                    f"""
Source: {page_url}

{text}
"""
                )

            if not contexts:
                return ("Unable to extract website content.")
            print(
                f"[BANK SEARCH] Built "
                f"{len(contexts)} contexts"
            )
            return "\n\n".join(contexts)
        except Exception as e:
            print(f"[SEARCH ERROR] {e}")
            return ( f"Search tool error: {str(e)}")

@tool
def google_search(
    query: str
) -> str:

    search_tool = GoogleSearchTool()
    return search_tool.search(
        query
    )
SEARCH_TOOLS = [
    google_search
]