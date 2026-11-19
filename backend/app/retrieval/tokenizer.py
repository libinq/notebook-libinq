import re
from typing import List

# Common English stop words
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "的", "了", "在", "是", "我",
    "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很",
    "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"
}

def tokenize_bilingual(text: str) -> List[str]:
    """
    Bilingual Chinese & English tokenization.
    - English words: converted to lowercase, tokenized by word boundary.
    - Chinese characters: broken into unigrams and overlapping bigrams for high-precision matching without heavy C-dependencies.
    """
    text = text.lower()
    tokens = []

    # 1. English / alphanumeric words
    english_words = re.findall(r'[a-z0-9_]+', text)
    for word in english_words:
        if len(word) > 1 and word not in STOP_WORDS:
            tokens.append(word)

    # 2. Chinese characters extraction
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    # Chinese unigrams
    for ch in chinese_chars:
        if ch not in STOP_WORDS:
            tokens.append(ch)
            
    # Chinese bigrams for contextual phrases
    chinese_text = "".join(re.findall(r'[\u4e00-\u9fa5]+', text))
    for i in range(len(chinese_text) - 1):
        bigram = chinese_text[i:i+2]
        if bigram not in STOP_WORDS:
            tokens.append(bigram)

    return tokens
