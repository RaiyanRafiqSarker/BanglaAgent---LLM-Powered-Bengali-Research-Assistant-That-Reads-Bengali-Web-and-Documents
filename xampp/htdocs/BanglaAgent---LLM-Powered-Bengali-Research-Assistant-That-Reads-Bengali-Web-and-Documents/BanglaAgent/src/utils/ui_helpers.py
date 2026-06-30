from typing import Optional
from config import FALLBACK_NO_EVIDENCE


PROGRESS_MESSAGES = {
    "pdf_reading": "PDF পড়া হচ্ছে...",
    "web_searching": "ওয়েব সোর্স খোঁজা হচ্ছে...",
    "retrieving": "প্রাসঙ্গিক তথ্য বের করা হচ্ছে...",
    "generating": "উত্তর তৈরি হচ্ছে...",
    "embedding": "ভেক্টর এমবেডিং তৈরি হচ্ছে...",
    "podcast": "পডকাস্ট স্ক্রিপ্ট লেখা হচ্ছে...",
}

NO_EVIDENCE_MSG = FALLBACK_NO_EVIDENCE


def format_sources_html(sources: list[dict]) -> str:
    if not sources:
        return "<p style='color:#aaa;'>কোনো সূত্র পাওয়া যায়নি।</p>"

    cards = []
    for i, s in enumerate(sources, 1):
        source_type = s.get("type", "unknown")
        if source_type == "pdf":
            icon = "📄"
            title = f"{s.get('filename', 'PDF')} — Page {s.get('page', '?')}"
            link = ""
        elif source_type == "web":
            icon = "🌐"
            title = s.get("title", "Web Source")
            url = s.get("url", "")
            link = f"<a href='{url}' target='_blank' style='color:#f59e0b;'>{url[:60]}...</a>" if url else ""
        else:
            icon = "📎"
            title = "Source"
            link = ""

        text_preview = s.get("text", "")[:200]
        if len(s.get("text", "")) > 200:
            text_preview += "..."

        card = f"""
        <div style="background:#1e293b; border-radius:8px; padding:12px; margin-bottom:8px; border-left:3px solid #f59e0b;">
            <div style="font-weight:600; color:#f8fafc;">{icon} [{i}] {title}</div>
            {f'<div style="margin-top:4px;">{link}</div>' if link else ''}
            <div style="color:#94a3b8; font-size:0.9em; margin-top:6px;">{text_preview}</div>
        </div>
        """
        cards.append(card)

    return "\n".join(cards)


def format_evidence_html(evidence: list[dict]) -> str:
    if not evidence:
        return "<p style='color:#aaa;'>কোনো প্রমাণ ব্যবহৃত হয়নি।</p>"

    items = []
    for i, e in enumerate(evidence, 1):
        text = e.get("text", "")[:300]
        source = ""
        if e.get("type") == "pdf":
            source = f"PDF: {e.get('filename', '?')}, page {e.get('page', '?')}"
        elif e.get("type") == "web":
            source = f"Web: {e.get('title', 'Unknown')}"

        item = f"""
        <div style="background:#0f172a; border-radius:6px; padding:10px; margin-bottom:6px;">
            <div style="color:#f59e0b; font-size:0.85em; font-weight:600;">Evidence {i} — {source}</div>
            <div style="color:#cbd5e1; font-size:0.9em; margin-top:4px;">{text}</div>
        </div>
        """
        items.append(item)

    return "\n".join(items)


def format_error_message(error: str) -> str:
    return f"""
    <div style="background:#7f1d1d; border-radius:8px; padding:16px; color:#fecaca;">
        <strong>⚠️ Error:</strong> {error}
    </div>
    """
