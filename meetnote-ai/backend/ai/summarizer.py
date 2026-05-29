
import re
from collections import Counter


def generate_summary(transcript, max_sentences=5):

    transcript = transcript.strip()
    if len(transcript) < 400:
        return transcript

    sentences = re.split(r'(?<=[.!?])\s+', transcript)
    words = re.findall(r"\w+", transcript.lower())
    if not sentences or not words:
        return transcript[:500] + "..."

    freq = Counter([w for w in words if len(w) > 3])
    sentence_scores = []
    for sentence in sentences:
        score = sum(freq[word] for word in re.findall(r"\w+", sentence.lower()) if len(word) > 3)
        sentence_scores.append((score, sentence.strip()))

    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    best_sentences = [sent for _, sent in sentence_scores[:max_sentences] if sent]

    if not best_sentences:
        return transcript[:500] + "..."

    best_sentences.sort(key=lambda s: transcript.find(s))
    summary = " ".join(best_sentences)

    if len(summary) < 120 and len(transcript) > 500:
        summary = transcript[:500].strip() + "..."

    return summary