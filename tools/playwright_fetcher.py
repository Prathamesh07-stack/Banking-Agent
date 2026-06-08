from playwright.sync_api import sync_playwright

class PlaywrightFetcher:

    def fetch_page(
        self,
        url: str
    ) -> str:

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True
                )
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )
                print(f"[PLAYWRIGHT] Fetching: {url}")

                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=30000
                )
                page.wait_for_timeout(5000)

                html = page.content()
                browser.close()
                return html

        except Exception as e:
            print(f"[PLAYWRIGHT ERROR] {url}")
            print(e)

            return ""