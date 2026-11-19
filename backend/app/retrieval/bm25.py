import math
from typing import List, Dict, Any, Tuple
from .tokenizer import tokenize_bilingual

class BM25Retriever:
    """
    BM25Okapi retriever for grounding chat and studio generations in notebook sources.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[Dict[str, Any]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def index(self, chunks: List[Dict[str, Any]]):
        self.corpus = chunks
        self.doc_lengths = []
        self.doc_freqs = {}
        self.idf = {}
        
        num_docs = len(chunks)
        if num_docs == 0:
            self.avg_doc_len = 0.0
            return

        total_length = 0
        for chunk in chunks:
            tokens = tokenize_bilingual(chunk["content"])
            chunk["tokens"] = tokens
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            # Calculate document frequencies
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_len = total_length / num_docs if num_docs > 0 else 0.0

        # Calculate IDF with floor protection
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log(1.0 + (num_docs - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 15) -> List[Dict[str, Any]]:
        if not self.corpus:
            return []

        query_tokens = tokenize_bilingual(query)
        if not query_tokens:
            return self.corpus[:top_k]

        scores = [0.0] * len(self.corpus)

        for i, chunk in enumerate(self.corpus):
            tokens = chunk.get("tokens", [])
            doc_len = self.doc_lengths[i]
            if doc_len == 0:
                continue

            # Token frequencies in this chunk
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            chunk_score = 0.0
            for qt in query_tokens:
                if qt in tf:
                    term_freq = tf[qt]
                    numerator = term_freq * (self.k1 + 1.0)
                    denominator = term_freq + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                    chunk_score += self.idf.get(qt, 0.0) * (numerator / denominator)

            scores[i] = chunk_score

        # Pair scores with chunk objects
        scored_chunks = [(score, self.corpus[idx]) for idx, score in enumerate(scores)]
        # Sort descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Filter out 0 scores if we have non-zero scores
        results = []
        for score, chunk in scored_chunks[:top_k]:
            result = dict(chunk)
            result["score"] = round(score, 4)
            results.append(result)

        return results
