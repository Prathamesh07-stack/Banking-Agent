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
        ],
        "credit": [
            "credit",
            "credit-card",
            "credit card",
            "cards"
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

        scored_links = []

        for link in links:
            score = 0
            url = (link["url"].lower())
            
            text = ( link["text"].lower())
            
            searchable = (url + " " + text)

            for keyword in keywords:
                if keyword in searchable:
                    score += 1
            # Priority 

            if "fd-interest-rate" in url:
                score += 50
            if "interest-rate" in url:
                score += 25
            if "interest-rates" in url:
                score += 25
            if "rate" in url:
                score += 10
            if "rates" in url:
                score += 10
            if "home-loan" in url:
                score += 20
            if "personal-loan" in url:
                score += 20
            if "fixed-deposit" in url:
                score += 15

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