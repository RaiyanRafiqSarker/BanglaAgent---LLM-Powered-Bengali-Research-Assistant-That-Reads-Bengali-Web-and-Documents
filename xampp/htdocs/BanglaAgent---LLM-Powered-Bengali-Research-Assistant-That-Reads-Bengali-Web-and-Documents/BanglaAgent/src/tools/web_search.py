import re
import logging
from bs4 import BeautifulSoup
import requests
from config import MAX_WEB_RESULTS, REQUEST_TIMEOUT
from src.utils.bengali_text import clean_bengali_text, remove_navigation_text

logger = logging.getLogger(__name__)

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
        logger.error("Neither 'ddgs' nor 'duckduckgo-search' is installed. Web search will not work.")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "bn,en;q=0.9",
}


def _ddg_search(query: str, max_results: int = 3) -> list[dict]:
    if DDGS is None:
        logger.warning("DDGS not available, skipping search")
        return []
    try:
        ddgs = DDGS()
        raw = list(ddgs.text(query, max_results=max_results))
        return raw
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for '{query[:60]}': {e}")
        return []


def _normalize_ddg_result(r: dict) -> dict:
    return {
        "title": r.get("title", ""),
        "url": r.get("href", "") or r.get("link", "") or r.get("url", ""),
        "snippet": r.get("body", "") or r.get("description", "") or r.get("snippet", ""),
    }


def _determine_evidence_strength(text: str, snippet: str) -> str:
    if text and text != snippet and len(text) > 200:
        return "moderate"
    return "weak"


def search_bengali_web(query: str, max_results: int = MAX_WEB_RESULTS) -> list[dict]:
    results = []

    prothom_results = search_prothom_alo(query)
    results.extend(prothom_results)

    daily_star_results = search_daily_star_bangla(query)
    results.extend(daily_star_results)

    if len(results) < max_results:
        fallback_results = fallback_search(query, max_results=max_results - len(results))
        results.extend(fallback_results)

    seen_urls = set()
    unique = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(r)

    logger.info(f"[WebSearch] Total unique results: {len(unique)} for query: {query[:60]}")
    return unique[:max_results]


def search_prothom_alo(query: str, max_results: int = 3) -> list[dict]:
    try:
        raw = _ddg_search(f"site:prothomalo.com {query}", max_results=max_results)
        results = []
        for r in raw:
            nr = _normalize_ddg_result(r)
            url = nr["url"]
            title = nr["title"]
            snippet = nr["snippet"]
            if not url or "prothomalo.com" not in url:
                continue
            article = scrape_article(url)
            text = article.get("text", "") or snippet
            if not text.strip():
                continue
            strength = _determine_evidence_strength(text, snippet)
            results.append({
                "type": "web",
                "title": title or article.get("title", "Prothom Alo Article"),
                "url": url,
                "text": text,
                "source_name": "Prothom Alo",
                "citation": f"[Source: {title or 'Prothom Alo'}, {url}]",
                "evidence_strength": strength,
                "source_type": "web",
            })
        logger.info(f"[WebSearch] Prothom Alo results: {len(results)}")
        return results
    except Exception as e:
        logger.warning(f"Prothom Alo search failed: {e}")
        return []


def search_daily_star_bangla(query: str, max_results: int = 3) -> list[dict]:
    try:
        raw = _ddg_search(f"site:bangla.thedailystar.net {query}", max_results=max_results)
        results = []
        for r in raw:
            nr = _normalize_ddg_result(r)
            url = nr["url"]
            title = nr["title"]
            snippet = nr["snippet"]
            if not url or "thedailystar" not in url:
                continue
            article = scrape_article(url)
            text = article.get("text", "") or snippet
            if not text.strip():
                continue
            strength = _determine_evidence_strength(text, snippet)
            results.append({
                "type": "web",
                "title": title or article.get("title", "Daily Star Bangla Article"),
                "url": url,
                "text": text,
                "source_name": "Daily Star Bangla",
                "citation": f"[Source: {title or 'Daily Star Bangla'}, {url}]",
                "evidence_strength": strength,
                "source_type": "web",
            })
        logger.info(f"[WebSearch] Daily Star Bangla results: {len(results)}")
        return results
    except Exception as e:
        logger.warning(f"Daily Star Bangla search failed: {e}")
        return []


def fallback_search(query: str, max_results: int = 5) -> list[dict]:
    try:
        raw = _ddg_search(f"{query} বাংলা বাংলাদেশ সংবাদ", max_results=max_results)
        results = []
        for r in raw:
            nr = _normalize_ddg_result(r)
            url = nr["url"]
            title = nr["title"]
            snippet = nr["snippet"]
            if not url:
                continue
            article = scrape_article(url)
            text = article.get("text", "") or snippet
            if not text.strip():
                continue
            strength = _determine_evidence_strength(text, snippet)
            results.append({
                "type": "web",
                "title": title or article.get("title", "Web Article"),
                "url": url,
                "text": text,
                "source_name": "Web",
                "citation": f"[Source: {title or 'Web'}, {url}]",
                "evidence_strength": strength,
                "source_type": "web",
            })
        logger.info(f"[WebSearch] Fallback results: {len(results)}")
        return results
    except Exception as e:
        logger.warning(f"Fallback search failed: {e}")
        return []


def scrape_article(url: str) -> dict:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html = resp.text
        return clean_article_text(html)
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return {"title": "", "text": ""}


def clean_article_text(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                      "iframe", "noscript", "form", "button", "svg"]):
        tag.decompose()

    for cls in ["advertisement", "ad-slot", "social-share", "related-news",
                 "comment", "sidebar", "menu", "nav-", "footer-"]:
        for el in soup.find_all(class_=re.compile(cls, re.I)):
            el.decompose()

    title = ""
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(strip=True)

    text = ""
    article = soup.find("article")
    if article:
        text = article.get_text(separator="\n", strip=True)
    else:
        main = soup.find("main") or soup.find(class_=re.compile(r"(content|article|story|body)", re.I))
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

    if text:
        text = clean_bengali_text(text)
        text = remove_navigation_text(text)

        noise_patterns = [
            r'বিজ্ঞাপন',
            r'আরও পড়ুন',
            r'(?i)share',
            r'(?i)follow\s*us',
        ]
        for pat in noise_patterns:
            text = re.sub(pat, '', text)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

    if len(text) > 5000:
        text = text[:5000]

    return {"title": title, "text": text}
