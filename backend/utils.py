import re, difflib
from textstat import flesch_reading_ease

def keyword_density(content, keyword):
    words = re.findall(r"\w+", content.lower())
    total = len(words) if words else 1
    kw_words = keyword.lower().split()
    count = 0
    for i in range(len(words)-len(kw_words)+1):
        if words[i:i+len(kw_words)] == kw_words:
            count += 1
    density = (count * len(kw_words)) / total * 100
    return round(density, 4)

def readability_score(content):
    try:
        return flesch_reading_ease(content)
    except Exception:
        return None

def simple_plagiarism_check(content, existing_texts):
    max_ratio = 0.0
    for t in existing_texts:
        s = difflib.SequenceMatcher(None, content, t).ratio()
        if s > max_ratio:
            max_ratio = s
    return max_ratio
