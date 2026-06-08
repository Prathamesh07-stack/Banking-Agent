class BankLinkRanker:

    BANKING_KEYWORDS = {
        "fd": [
            "fd",
            "fixed",
            "fixed-deposit",
            "fixed deposit",
            "deposit",
            "deposits",
            "term-deposit",
            "term deposit"
        ],
        "loan": [
            "loan",
            "loans",
            "home-loan",
            "home loan",
            "personal-loan",
            "personal loan",
            "vehicle-loan",
            "mortgage"
        ],
        "interest": [
            "interest",
            "rate",
            "rates",
            "interest-rate",
            "interest-rates"
        ]
    }

    def expand_keywords(
        self,
        query: str
    ) -> list[str]:

        keywords = []

        query_lower = query.lower()

        for word in query_lower.split():

            keywords.append(word)

            if word in self.BANKING_KEYWORDS:
                keywords.extend(
                    self.BANKING_KEYWORDS[word]
                )

        return list(set(keywords))

    def rank_links(
        self,
        links: list[dict],
        query: str
    ) -> list[str]:

        keywords = self.expand_keywords(
            query
        )

        query_lower = query.lower()

        scored_links = []

        for link in links:

            score = 0

            url = (
                link["url"].lower()
            )

            text = (
                link["text"].lower()
            )

            searchable = (
                url + " " + text
            )

            # Base keyword matching
            for keyword in keywords:

                if keyword in searchable:
                    score += 1

            # FD Queries
            if (
                "fd" in query_lower
                or "fixed deposit" in query_lower
                or "deposit" in query_lower
            ):

                if "fd-interest-rate" in url:
                    score += 150

                if "fixed-deposit" in url:
                    score += 120

                if "deposit-rates" in url:
                    score += 100

                if "term-deposit" in url:
                    score += 80

                if "interest-rate" in url:
                    score += 40

                if "interest-rates" in url:
                    score += 40

            # Loan Queries
            if "loan" in query_lower:

                # Home Loan Queries
                if "home loan" in query_lower:

                    if "home-loan" in url:
                        score += 200

                    if "personal-loan" in url:
                        score -= 50

                # Personal Loan Queries
                if "personal loan" in query_lower:

                    if "personal-loan" in url:
                        score += 200

                    if "home-loan" in url:
                        score -= 50

                if "personal-loan" in url:
                    score += 120

                if "home-loan" in url:
                    score += 120

                if "vehicle-loan" in url:
                    score += 80

                if "mortgage" in url:
                    score += 80

                if "loan" in url:
                    score += 50

            # Generic Interest Queries
            if (
                "interest" in query_lower
                or "rate" in query_lower
            ):

                if (
                    "loan" not in query_lower
                    and "fd" not in query_lower
                    and "deposit" not in query_lower
                ):

                    if "interest-rate" in url:
                        score += 20

                    if "interest-rates" in url:
                        score += 20

                    if "rate" in url:
                        score += 10

                    if "rates" in url:
                        score += 10

            if score > 0:

                scored_links.append(
                    (
                        score,
                        link["url"]
                    )
                )

        scored_links.sort(
            reverse=True
        )

        return [
            url
            for score, url
            in scored_links[:5]
        ]