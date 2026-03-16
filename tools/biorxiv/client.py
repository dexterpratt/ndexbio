"""bioRxiv API client for discovering and retrieving preprints.

Uses the bioRxiv API (https://api.biorxiv.org) to search for recent papers
and retrieve full-text content via the published DOI or direct PDF links.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

import requests


BIORXIV_API_BASE = "https://api.biorxiv.org"
BIORXIV_CONTENT_URL = "https://www.biorxiv.org/content"


@dataclass
class BiorxivPaper:
    """Represents a bioRxiv preprint with metadata and optional content."""

    doi: str
    title: str
    authors: str
    abstract: str
    category: str
    date: str  # YYYY-MM-DD
    version: str
    jatsxml: str = ""  # URL to JATS XML full text if available
    published_doi: str = ""  # DOI of the published version if any
    biorxiv_url: str = ""

    def to_dict(self) -> dict:
        return {
            "doi": self.doi,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "category": self.category,
            "date": self.date,
            "version": self.version,
            "jatsxml": self.jatsxml,
            "published_doi": self.published_doi,
            "biorxiv_url": self.biorxiv_url,
        }


class BiorxivClient:
    """Client for the bioRxiv API.

    Supports listing recent papers by date range and subject area,
    and retrieving paper details.
    """

    def __init__(self, rate_limit_delay: float = 1.0):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "ndexbio-agents/0.1 (https://github.com/ndexbio/ndexbio)"
        })
        self._rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str) -> dict:
        """Make a rate-limited GET request."""
        self._rate_limit()
        resp = self._session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_recent_papers(
        self,
        interval_days: int = 7,
        server: str = "biorxiv",
        cursor: int = 0,
        page_size: int = 100,
    ) -> list[BiorxivPaper]:
        """Fetch papers posted in the last N days.

        Args:
            interval_days: How many days back to search.
            server: 'biorxiv' or 'medrxiv'.
            cursor: Pagination cursor (0-based).
            page_size: Results per page (max 100).

        Returns:
            List of BiorxivPaper objects.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=interval_days)
        return self.get_papers_by_date(
            start_date.isoformat(),
            end_date.isoformat(),
            server=server,
            cursor=cursor,
            page_size=page_size,
        )

    def get_papers_by_date(
        self,
        start_date: str,
        end_date: str,
        server: str = "biorxiv",
        cursor: int = 0,
        page_size: int = 100,
    ) -> list[BiorxivPaper]:
        """Fetch papers posted between two dates.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            server: 'biorxiv' or 'medrxiv'.
            cursor: Pagination cursor.
            page_size: Results per page.
        """
        url = (
            f"{BIORXIV_API_BASE}/details/{server}/"
            f"{start_date}/{end_date}/{cursor}"
        )
        data = self._get(url)
        collection = data.get("collection", [])

        papers = []
        for item in collection[:page_size]:
            paper = BiorxivPaper(
                doi=item.get("doi", ""),
                title=item.get("title", ""),
                authors=item.get("authors", ""),
                abstract=item.get("abstract", ""),
                category=item.get("category", ""),
                date=item.get("date", ""),
                version=str(item.get("version", "1")),
                jatsxml=item.get("jatsxml", ""),
                published_doi=item.get("published", ""),
                biorxiv_url=f"{BIORXIV_CONTENT_URL}/{item.get('doi', '')}",
            )
            papers.append(paper)

        return papers

    def get_all_recent_papers(
        self,
        interval_days: int = 7,
        server: str = "biorxiv",
        max_papers: int = 500,
    ) -> list[BiorxivPaper]:
        """Fetch all papers from the last N days, handling pagination.

        Args:
            interval_days: How many days back to search.
            server: 'biorxiv' or 'medrxiv'.
            max_papers: Maximum total papers to retrieve.
        """
        all_papers = []
        cursor = 0

        while len(all_papers) < max_papers:
            batch = self.get_recent_papers(
                interval_days=interval_days,
                server=server,
                cursor=cursor,
            )
            if not batch:
                break
            all_papers.extend(batch)
            cursor += len(batch)

        return all_papers[:max_papers]

    def search_by_keywords(
        self,
        papers: list[BiorxivPaper],
        keywords: list[str],
        match_mode: str = "any",
    ) -> list[BiorxivPaper]:
        """Filter papers by keyword matching in title and abstract.

        Args:
            papers: Papers to filter.
            keywords: Keywords to search for.
            match_mode: 'any' (at least one keyword) or 'all' (all keywords).

        Returns:
            Filtered list of papers matching keyword criteria.
        """
        results = []
        for paper in papers:
            searchable = f"{paper.title} {paper.abstract}".lower()
            if match_mode == "all":
                if all(kw.lower() in searchable for kw in keywords):
                    results.append(paper)
            else:
                if any(kw.lower() in searchable for kw in keywords):
                    results.append(paper)
        return results

    def get_paper_fulltext_url(self, paper: BiorxivPaper) -> str:
        """Get the URL for the full text (JATS XML or HTML) of a paper."""
        if paper.jatsxml:
            return paper.jatsxml
        # Fall back to the HTML version
        return f"{paper.biorxiv_url}.full"

    def fetch_paper_text(self, paper: BiorxivPaper) -> str:
        """Attempt to retrieve the full text of a paper.

        Tries JATS XML first, then falls back to scraping the HTML full text.
        Returns raw text content (stripped of XML/HTML tags for readability).
        """
        # Try JATS XML first
        if paper.jatsxml:
            try:
                self._rate_limit()
                resp = self._session.get(paper.jatsxml, timeout=30)
                resp.raise_for_status()
                # Strip XML tags for a readable text version
                text = re.sub(r"<[^>]+>", " ", resp.text)
                text = re.sub(r"\s+", " ", text).strip()
                return text
            except Exception:
                pass

        # Fall back to HTML full text
        url = f"{paper.biorxiv_url}.full"
        try:
            self._rate_limit()
            resp = self._session.get(url, timeout=30)
            resp.raise_for_status()
            # Extract article body text (rough extraction)
            text = re.sub(r"<script[^>]*>.*?</script>", "", resp.text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception as e:
            return f"Error fetching full text: {e}"
