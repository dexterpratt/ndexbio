"""bioRxiv MCP Server — exposes bioRxiv paper discovery as MCP tools.

Run with:  python -m tools.biorxiv.server
"""

import json
from mcp.server.fastmcp import FastMCP
from .client import BiorxivClient

mcp = FastMCP("biorxiv", log_level="INFO")

_client: BiorxivClient | None = None


def _get_client() -> BiorxivClient:
    global _client
    if _client is None:
        _client = BiorxivClient()
    return _client


# ── Paper Discovery ──────────────────────────────────────────────────


@mcp.tool()
def search_recent_papers(
    keywords: str,
    interval_days: int = 7,
    match_mode: str = "any",
    max_results: int = 50,
) -> dict:
    """Search recent bioRxiv preprints by keywords in title and abstract.

    Args:
        keywords: Comma-separated keywords (e.g. "influenza, host-pathogen, innate immunity").
        interval_days: How many days back to search (default 7).
        match_mode: "any" (at least one keyword matches) or "all" (all must match).
        max_results: Maximum papers to return after filtering.
    """
    try:
        client = _get_client()
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not kw_list:
            return {"status": "error", "message": "No keywords provided"}

        all_papers = client.get_all_recent_papers(
            interval_days=interval_days, max_papers=500
        )
        matched = client.search_by_keywords(all_papers, kw_list, match_mode=match_mode)
        matched = matched[:max_results]

        return {
            "status": "success",
            "data": {
                "total_scanned": len(all_papers),
                "matched": len(matched),
                "papers": [p.to_dict() for p in matched],
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}


@mcp.tool()
def get_recent_papers_by_category(
    category: str = "microbiology",
    interval_days: int = 7,
    max_results: int = 50,
) -> dict:
    """Get recent bioRxiv papers filtered by subject category.

    Args:
        category: bioRxiv category (e.g. "microbiology", "immunology",
                  "bioinformatics", "cell biology", "molecular biology").
        interval_days: How many days back to search.
        max_results: Maximum papers to return.
    """
    try:
        client = _get_client()
        all_papers = client.get_all_recent_papers(
            interval_days=interval_days, max_papers=500
        )
        filtered = [
            p for p in all_papers
            if category.lower() in p.category.lower()
        ][:max_results]

        return {
            "status": "success",
            "data": {
                "total_scanned": len(all_papers),
                "matched": len(filtered),
                "papers": [p.to_dict() for p in filtered],
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}


@mcp.tool()
def get_paper_fulltext(doi: str) -> dict:
    """Retrieve the full text of a bioRxiv paper by DOI.

    Args:
        doi: The bioRxiv DOI (e.g. "10.1101/2026.01.15.123456").
    """
    try:
        client = _get_client()
        paper = _find_paper_by_doi(client, doi)
        if paper is None:
            # Construct a minimal paper object for fetching
            from .client import BiorxivPaper, BIORXIV_CONTENT_URL
            paper = BiorxivPaper(
                doi=doi,
                title="",
                authors="",
                abstract="",
                category="",
                date="",
                version="1",
                biorxiv_url=f"{BIORXIV_CONTENT_URL}/{doi}",
            )

        text = client.fetch_paper_text(paper)
        return {
            "status": "success",
            "data": {
                "doi": doi,
                "title": paper.title,
                "text_length": len(text),
                "text": text[:50000],  # Cap at 50k chars
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}


@mcp.tool()
def get_paper_abstract(doi: str) -> dict:
    """Get the abstract and metadata for a specific bioRxiv paper by DOI.

    Args:
        doi: The bioRxiv DOI.
    """
    try:
        client = _get_client()
        paper = _find_paper_by_doi(client, doi)
        if paper is None:
            return {"status": "error", "message": f"Paper with DOI {doi} not found"}

        return {"status": "success", "data": paper.to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}


def _find_paper_by_doi(client: BiorxivClient, doi: str):
    """Look up a paper by DOI using the details endpoint."""
    from .client import BiorxivPaper, BIORXIV_CONTENT_URL

    url = f"https://api.biorxiv.org/details/biorxiv/{doi}"
    try:
        data = client._get(url)
        collection = data.get("collection", [])
        if collection:
            item = collection[-1]  # Latest version
            return BiorxivPaper(
                doi=item.get("doi", doi),
                title=item.get("title", ""),
                authors=item.get("authors", ""),
                abstract=item.get("abstract", ""),
                category=item.get("category", ""),
                date=item.get("date", ""),
                version=str(item.get("version", "1")),
                jatsxml=item.get("jatsxml", ""),
                published_doi=item.get("published", ""),
                biorxiv_url=f"{BIORXIV_CONTENT_URL}/{doi}",
            )
    except Exception:
        pass
    return None


# ── Entry point ──────────────────────────────────────────────────────

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
