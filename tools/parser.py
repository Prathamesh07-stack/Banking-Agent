from bs4 import BeautifulSoup

class ContentParser:

    def extract_text(
        self,
        html: str,
        max_chars: int = 5000
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

        # Prefer main content areas
        content = (
            soup.find("article")
            or soup.find("main")
            or soup.find("section")
        )

        if content:
            text = content.get_text(
                separator=" ",
                strip=True
            )
        else:
            text = soup.get_text(
                separator=" ",
                strip=True
            )

        # Explicitly extract table data
        tables = []

        for table in soup.find_all("table"):

            table_text = table.get_text(
                separator=" ",
                strip=True
            )

            if table_text:
                tables.append(
                    table_text
                )

        if tables:
            text += "\n\n" + "\n".join(
                tables
            )

        text = " ".join(
            text.split()
        )

        return text[:max_chars]