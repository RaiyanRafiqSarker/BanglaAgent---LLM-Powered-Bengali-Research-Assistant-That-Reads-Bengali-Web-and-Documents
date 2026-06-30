import re
from typing import Optional


def clean_bengali_text(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'(?<=\n) +', '', text)
    return text.strip()


def is_bengali_text(text: str) -> bool:
    bengali_chars = len(re.findall(r'[ঀ-৿]', text))
    total_alpha = len(re.findall(r'[a-zA-Zঀ-৿]', text))
    if total_alpha == 0:
        return False
    return (bengali_chars / total_alpha) > 0.3


def normalize_bengali_numerals(text: str) -> str:
    bn_digits = '০১২৩৪৫৬৭৮৯'
    en_digits = '0123456789'
    table = str.maketrans(bn_digits, en_digits)
    return text.translate(table)


def truncate_text(text: str, max_chars: int = 3000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def remove_navigation_text(text: str) -> str:
    nav_patterns = [
        r'(?i)(menu|navigation|sidebar|footer|header|copyright|advertisement|related\s*articles?)',
        r'(?i)(share\s*on|follow\s*us|subscribe|newsletter|sign\s*up)',
        r'(?i)(privacy\s*policy|terms\s*of\s*(use|service)|cookie)',
        r'সর্বশেষ\s*খবর',
        r'আরও\s*পড়ুন',
        r'মন্তব্য\s*করুন',
        r'শেয়ার\s*করুন',
    ]
    lines = text.split('\n')
    filtered = []
    for line in lines:
        line_stripped = line.strip()
        if len(line_stripped) < 10:
            continue
        skip = False
        for pattern in nav_patterns:
            if re.search(pattern, line_stripped):
                skip = True
                break
        if not skip:
            filtered.append(line)
    return '\n'.join(filtered)


def format_bengali_answer(
    summary: str,
    details: str,
    key_points: list[str],
    sources: list[str],
    limitations: Optional[str] = None,
) -> str:
    sections = []
    sections.append(f"## সংক্ষিপ্ত উত্তর\n{summary}")
    sections.append(f"## বিস্তারিত ব্যাখ্যা\n{details}")

    if key_points:
        bullets = '\n'.join(f"- {p}" for p in key_points)
        sections.append(f"## মূল পয়েন্ট\n{bullets}")

    if sources:
        numbered = '\n'.join(f"{i+1}. {s}" for i, s in enumerate(sources))
        sections.append(f"## সূত্র\n{numbered}")

    if limitations:
        sections.append(f"## সীমাবদ্ধতা\n{limitations}")

    return '\n\n'.join(sections)
