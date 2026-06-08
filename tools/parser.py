from bs4 import BeautifulSoup

class ContentParser:

    def extract_text(
        self,
        html: str,
        max_chars: int = 1500
    ) -> str:

        if not html:
            return ""

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "noscript"
        ]):
            tag.decompose()

        article = soup.find("article")

        if article:
            text = article.get_text(
                separator=" ",
                strip=True
            )
        else:
            text = soup.get_text(
                separator=" ",
                strip=True
            )

        text = " ".join(text.split())
        return text[:max_chars]