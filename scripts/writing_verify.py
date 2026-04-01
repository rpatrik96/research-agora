#!/usr/bin/env python3
"""Compute writing quality metrics for scientific text."""

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

FILLER_WORDS = {
    "basically", "simply", "just", "actually", "really", "very",
    "quite", "rather", "somewhat", "perhaps", "fairly",
    "literally", "essentially", "obviously", "clearly", "certainly",
    "definitely", "practically",
}

FILLER_PHRASES = [
    "in order to", "it should be noted that", "it is important to note that",
    "it is worth noting that", "as a matter of fact", "it goes without saying",
    "needless to say", "at the end of the day", "for all intents and purposes",
    "in the final analysis", "it can be seen that", "as we all know",
    "it is well known that", "it is interesting to note that",
]

HEDGE_WORDS = {
    "might", "may", "could", "possibly", "potentially", "perhaps",
    "seemingly", "apparently", "arguably", "presumably", "conceivably",
    "likely", "unlikely", "probable", "plausible",
}

HEDGE_PHRASES = [
    "to some extent", "in some cases", "it is possible that",
    "it seems that", "it appears that", "we believe that",
    "it is likely that", "we feel that", "one might argue",
    "it could be argued", "there is reason to believe",
]

WEAK_OPENERS = [
    "it is", "it was", "there is", "there are", "there was", "there were",
    "it has been", "it should be noted", "it is important",
    "it is worth", "it is interesting", "it can be seen",
    "as we all know", "as is well known",
]

ML_JARGON = {
    "transformer", "attention", "self-attention", "cross-attention",
    "encoder", "decoder", "embedding", "tokenizer", "softmax",
    "backpropagation", "gradient descent", "stochastic gradient descent",
    "batch normalization", "layer normalization", "dropout",
    "convolution", "pooling", "recurrent", "lstm", "gru",
    "generative", "discriminative", "adversarial", "contrastive",
    "variational", "autoencoder", "diffusion", "latent",
    "fine-tuning", "pre-training", "transfer learning",
    "regularization", "overfitting", "underfitting",
    "hyperparameter", "epoch", "batch size", "learning rate",
    "loss function", "objective function", "optimization",
    "inference", "training", "evaluation",
    "equivariant", "invariant", "disentangled",
    "causal", "counterfactual", "interventional",
}

SECTION_PATTERNS = {
    "abstract": r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
    "introduction": r"\\section\{Introduction\}",
    "related_work": r"\\section\{Related Work\}",
    "methods": r"\\section\{(?:Method|Approach|Model)\w*\}",
    "experiments": r"\\section\{Experiment\w*\}",
    "results": r"\\section\{Result\w*\}",
    "discussion": r"\\section\{Discussion\w*\}",
    "conclusion": r"\\section\{Conclusion\w*\}",
}

SECTION_THRESHOLDS = {
    "abstract":     {"fk_grade": (10, 14), "max_passive_pct": 15, "max_sentence_length": 35, "max_jargon_per_para": 2},
    "introduction": {"fk_grade": (12, 14), "max_passive_pct": 20, "max_sentence_length": 40, "max_jargon_per_para": 3},
    "methods":      {"fk_grade": (14, 18), "max_passive_pct": 35, "max_sentence_length": 50, "max_jargon_per_para": 5},
    "experiments":  {"fk_grade": (12, 16), "max_passive_pct": 30, "max_sentence_length": 45, "max_jargon_per_para": 4},
    "conclusion":   {"fk_grade": (12, 14), "max_passive_pct": 15, "max_sentence_length": 35, "max_jargon_per_para": 2},
    "_default":     {"fk_grade": (12, 16), "max_passive_pct": 25, "max_sentence_length": 40, "max_jargon_per_para": 4},
}

PASSIVE_PATTERN = re.compile(
    r'\b(?:is|are|was|were|be|been|being)\s+'
    r'(?:\w+\s+){0,3}'
    r'(?:\w+ed|written|given|taken|driven|spoken|chosen|known|shown|grown|drawn|thrown|blown|sewn|done|gone|run|seen|eaten|come|become|gotten|set|put|cut|hit|let|built|sent|spent|left|lost|found|kept|thought|brought|bought|taught|caught|fought|sought|held|told|sold|read|heard|stood|understood|met|begun|broken|fallen|forgotten|hidden|risen|shaken|stolen|woken|worn|wound|bound|fed|fled|hung|led|lit|paid|said|sat|shot|slid|slung|spun|stung|struck|stuck|swum|swung|torn|woven|wound)\b',
    re.IGNORECASE,
)

# Abbreviations to protect before sentence splitting
_ABBREV = (
    r"(?:Mr|Mrs|Dr|Prof|Jr|Sr|vs|etc|Fig|Eq|Tab|et\s+al|i\.e|e\.g"
    r"|cf|approx|est|dept|avg|max|min|std|Sec|App|Alg|Def|Thm|Prop|Lem|Cor)\."
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SentenceMetrics:
    text: str
    word_count: int
    is_passive: bool
    hedge_count: int
    filler_count: int
    starts_with_weak_opener: bool


@dataclass
class ParagraphMetrics:
    sentences: list
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    sentence_length_variance: float
    passive_ratio: float
    hedge_density: float
    filler_density: float
    opening_sentence_word_count: int
    jargon_count: int


@dataclass
class SectionMetrics:
    name: str
    paragraphs: list
    word_count: int
    paragraph_count: int
    avg_paragraph_length: float


@dataclass
class DocumentMetrics:
    total_words: int
    total_sentences: int
    total_paragraphs: int
    flesch_kincaid_grade: float
    avg_sentence_length: float
    sentence_length_std: float
    long_sentences: int
    very_long_sentences: int
    jargon_density: float
    passive_voice_pct: float
    hedge_density: float
    filler_density: float
    filler_inventory: dict
    hedge_inventory: dict
    weak_openers: int
    sentence_length_cv: float
    monotony_score: float
    short_sentence_pct: float
    medium_sentence_pct: float
    long_sentence_pct: float
    avg_paragraph_length: float
    paragraph_length_std: float
    sections: list
    opening_sentences: list
    longest_sentences: list
    hedge_examples: list
    passive_examples: list
    filler_examples: list
    input_hash: str
    timestamp: str


# ---------------------------------------------------------------------------
# LaTeX stripping
# ---------------------------------------------------------------------------

def strip_latex(text: str) -> str:
    """Strip LaTeX markup, returning plain prose with section markers preserved."""
    # Remove block environments that aren't prose
    for env in ("equation", "align", "gather", "multline", "eqnarray"):
        text = re.sub(
            rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}",
            " [EQUATION] ", text, flags=re.DOTALL
        )
    for env in ("figure", "table", "algorithm", "lstlisting", "verbatim"):
        text = re.sub(
            rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}",
            " ", text, flags=re.DOTALL
        )

    # Replace citation/ref commands
    text = re.sub(r"\\(?:cite|cref|ref|eqref|autoref)\*?\{[^}]*\}", "[REF]", text)

    # Replace section/subsection titles with a plain marker (preserve content)
    def _sec_title(m):
        inner = re.sub(r"\\[a-zA-Z]+\s*", "", m.group(2)).strip()
        return f"\n\n## {inner}\n\n"
    text = re.sub(
        r"\\(section|subsection|subsubsection)\*?\s*\{([^}]*)\}",
        _sec_title, text
    )

    # Abstract environment — keep text
    text = re.sub(r"\\begin\{abstract\}", "\n\n## Abstract\n\n", text)
    text = re.sub(r"\\end\{abstract\}", "\n\n", text)

    # Remove math mode
    text = re.sub(r"\$\$.*?\$\$", " [EQUATION] ", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$\n]+\$", " ", text)
    text = re.sub(r"\\\[.*?\\\]", " [EQUATION] ", text, flags=re.DOTALL)

    # From parse_latex.py line 144 — generic command stripping
    text = re.sub(r"\\[a-zA-Z]+\*?\s*(\[[^\]]*\])?\s*\{([^}]*)\}", r" \2 ", text)

    # Remaining bare commands
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)

    # Curly braces, special chars
    text = re.sub(r"[{}]", " ", text)
    text = re.sub(r"~", " ", text)
    text = re.sub(r"--+", "-", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def strip_markdown(text: str) -> str:
    """Strip Markdown formatting."""
    # Code blocks
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Headers — keep as section markers
    text = re.sub(r"^(#{1,6})\s+(.+)$", r"\n\n## \2\n\n", text, flags=re.MULTILINE)
    # Links and images
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\(.*?\)", r"\1", text)
    # Bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_format(path: Optional[str], text: str) -> str:
    if path and path.endswith(".tex"):
        return "latex"
    if path and path.endswith(".md"):
        return "markdown"
    if re.search(r"\\documentclass|\\begin\{document\}", text):
        return "latex"
    if re.search(r"^# ", text, re.MULTILINE):
        return "markdown"
    return "text"


def prepare_text(raw: str, fmt: str) -> tuple:
    """Return (plain_text, sections_dict) where sections_dict maps name->text."""
    if fmt == "latex":
        sections = _extract_latex_sections(raw)
        plain = strip_latex(raw)
    elif fmt == "markdown":
        sections = _extract_markdown_sections(raw)
        plain = strip_markdown(raw)
    else:
        sections = {"_full": raw}
        plain = raw
    return plain, sections


def _extract_latex_sections(text: str) -> dict:
    sections = {}
    # Abstract
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.DOTALL)
    if m:
        sections["abstract"] = strip_latex(m.group(1))

    # Named sections
    sec_re = re.compile(
        r"\\(?:section|subsection)\*?\s*\{([^}]+)\}(.*?)(?=\\(?:section|subsection)\*?\s*\{|\Z)",
        re.DOTALL
    )
    for m in sec_re.finditer(text):
        title = m.group(1).strip().lower().replace(" ", "_")
        sections[title] = strip_latex(m.group(2))
    return sections


def _extract_markdown_sections(text: str) -> dict:
    sections = {}
    parts = re.split(r"^(#{1,3}\s+.+)$", text, flags=re.MULTILINE)
    current = "_preamble"
    buf = []
    for part in parts:
        if re.match(r"^#{1,3}\s+", part):
            if buf:
                sections[current] = strip_markdown("\n".join(buf))
            current = re.sub(r"^#+\s+", "", part).strip().lower().replace(" ", "_")
            buf = []
        else:
            buf.append(part)
    if buf:
        sections[current] = strip_markdown("\n".join(buf))
    return sections


# ---------------------------------------------------------------------------
# NLP helpers
# ---------------------------------------------------------------------------

_ABBREV_RE = re.compile(_ABBREV, re.IGNORECASE)

def split_sentences(text: str) -> list:
    placeholder = "\x00"
    protected = _ABBREV_RE.sub(lambda m: m.group().replace(".", placeholder), text)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', protected)
    return [p.replace(placeholder, ".").strip() for p in parts if p.strip()]


def count_words_plain(text: str) -> int:
    return len(re.findall(r"\b[a-zA-Z']+\b", text))


def count_syllables(word: str) -> int:
    word = word.lower().rstrip("es")
    count = len(re.findall(r"[aeiou]+", word))
    return max(1, count)


def flesch_kincaid_grade(sentences: list) -> float:
    total_words = sum(count_words_plain(s) for s in sentences)
    total_syllables = sum(
        count_syllables(w)
        for s in sentences
        for w in re.findall(r"\b[a-zA-Z']+\b", s)
    )
    n = len(sentences)
    if n == 0 or total_words == 0:
        return 0.0
    return 0.39 * (total_words / n) + 11.8 * (total_syllables / total_words) - 15.59


def is_passive(sentence: str) -> bool:
    return bool(PASSIVE_PATTERN.search(sentence))


def _count_items(text: str, words: set, phrases: list) -> tuple:
    """Return (total_count, inventory_dict)."""
    low = text.lower()
    inv: dict = {}
    total = 0
    for ph in phrases:
        c = low.count(ph)
        if c:
            inv[ph] = c
            total += c
    for w in words:
        c = len(re.findall(rf"\b{re.escape(w)}\b", low))
        if c:
            inv[w] = inv.get(w, 0) + c
            total += c
    return total, inv


def count_fillers(text: str) -> tuple:
    return _count_items(text, FILLER_WORDS, FILLER_PHRASES)


def count_hedges(text: str) -> tuple:
    return _count_items(text, HEDGE_WORDS, HEDGE_PHRASES)


def count_jargon(text: str) -> int:
    low = text.lower()
    return sum(
        len(re.findall(rf"\b{re.escape(j)}\b", low))
        for j in ML_JARGON
    )


def starts_with_weak(sentence: str) -> bool:
    low = sentence.strip().lower()
    return any(low.startswith(w) for w in WEAK_OPENERS)


def monotony_score(lengths: list) -> float:
    if len(lengths) < 2:
        return 0.0
    buckets = ["S" if n < 12 else ("M" if n <= 25 else "L") for n in lengths]
    # max run length
    max_run = cur_run = 1
    for i in range(1, len(buckets)):
        if buckets[i] == buckets[i - 1]:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    # same-bucket pair ratio
    same_pairs = sum(1 for i in range(1, len(buckets)) if buckets[i] == buckets[i - 1])
    pair_ratio = same_pairs / (len(buckets) - 1)
    run_score = min(1.0, (max_run - 1) / max(1, len(lengths) - 1))
    return 0.5 * run_score + 0.5 * pair_ratio


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def _analyze_paragraph(raw_para: str) -> ParagraphMetrics:
    sents = split_sentences(raw_para)
    if not sents:
        sents = [raw_para]
    sm_list = []
    for s in sents:
        wc = count_words_plain(s)
        fc, _ = count_fillers(s)
        hc, _ = count_hedges(s)
        sm_list.append(SentenceMetrics(
            text=s, word_count=wc, is_passive=is_passive(s),
            hedge_count=hc, filler_count=fc,
            starts_with_weak_opener=starts_with_weak(s),
        ))
    wcs = [s.word_count for s in sm_list]
    total_w = sum(wcs)
    avg_len = total_w / len(wcs) if wcs else 0.0
    variance = (sum((x - avg_len) ** 2 for x in wcs) / len(wcs)) if len(wcs) > 1 else 0.0
    passive_ratio = sum(1 for s in sm_list if s.is_passive) / len(sm_list)
    hedge_d = (sum(s.hedge_count for s in sm_list) / total_w * 100) if total_w else 0.0
    filler_d = (sum(s.filler_count for s in sm_list) / total_w * 100) if total_w else 0.0
    return ParagraphMetrics(
        sentences=sm_list,
        word_count=total_w,
        sentence_count=len(sm_list),
        avg_sentence_length=avg_len,
        sentence_length_variance=variance,
        passive_ratio=passive_ratio,
        hedge_density=hedge_d,
        filler_density=filler_d,
        opening_sentence_word_count=wcs[0] if wcs else 0,
        jargon_count=count_jargon(raw_para),
    )


def _split_paragraphs(text: str) -> list:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def analyze_document(text: str, fmt: str) -> DocumentMetrics:
    """Main entry point. Strips markup, computes all metrics, returns DocumentMetrics."""
    plain, sections_raw = prepare_text(text, fmt)
    input_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
    ts = datetime.now(timezone.utc).isoformat()

    paragraphs_raw = _split_paragraphs(plain)
    all_para_metrics = [_analyze_paragraph(p) for p in paragraphs_raw if p]

    all_sentences: list = []
    for pm in all_para_metrics:
        all_sentences.extend(pm.sentences)

    total_words = sum(pm.word_count for pm in all_para_metrics)
    total_sentences = len(all_sentences)
    total_paragraphs = len(all_para_metrics)

    sent_lengths = [s.word_count for s in all_sentences]
    avg_sl = total_words / total_sentences if total_sentences else 0.0
    std_sl = (
        (sum((n - avg_sl) ** 2 for n in sent_lengths) / total_sentences) ** 0.5
        if total_sentences else 0.0
    )
    sl_cv = std_sl / avg_sl if avg_sl else 0.0

    long_sents = sum(1 for n in sent_lengths if n > 40)
    very_long_sents = sum(1 for n in sent_lengths if n > 60)
    _ts = total_sentences or 1
    short_pct = sum(1 for n in sent_lengths if n < 12) / _ts * 100
    med_pct = sum(1 for n in sent_lengths if 12 <= n <= 25) / _ts * 100
    long_pct = sum(1 for n in sent_lengths if n > 25) / _ts * 100
    if not total_sentences:
        short_pct = med_pct = long_pct = 0.0

    fk = flesch_kincaid_grade([s.text for s in all_sentences])
    passive_pct = sum(1 for s in all_sentences if s.is_passive) / total_sentences * 100 if total_sentences else 0.0

    _, filler_inv = count_fillers(plain)
    _, hedge_inv = count_hedges(plain)
    total_fillers = sum(filler_inv.values())
    total_hedges = sum(hedge_inv.values())
    filler_d = total_fillers / total_words * 100 if total_words else 0.0
    hedge_d = total_hedges / total_words * 100 if total_words else 0.0
    weak_openers = sum(1 for s in all_sentences if s.starts_with_weak_opener)

    total_jargon = sum(pm.jargon_count for pm in all_para_metrics)
    jargon_density = total_jargon / total_paragraphs if total_paragraphs else 0.0

    para_word_counts = [pm.word_count for pm in all_para_metrics]
    avg_para_len = sum(para_word_counts) / total_paragraphs if total_paragraphs else 0.0
    para_std = (
        (sum((x - avg_para_len) ** 2 for x in para_word_counts) / total_paragraphs) ** 0.5
        if total_paragraphs else 0.0
    )

    mono = monotony_score(sent_lengths)

    # Build section metrics
    sec_metrics = []
    for sec_name, sec_text in sections_raw.items():
        sec_paras_raw = _split_paragraphs(sec_text)
        sec_paras = [_analyze_paragraph(p) for p in sec_paras_raw if p]
        sw = sum(pm.word_count for pm in sec_paras)
        sec_metrics.append(SectionMetrics(
            name=sec_name,
            paragraphs=sec_paras,
            word_count=sw,
            paragraph_count=len(sec_paras),
            avg_paragraph_length=sw / len(sec_paras) if sec_paras else 0.0,
        ))

    # Raw examples for LLM
    opening_sentences = [pm.sentences[0].text for pm in all_para_metrics if pm.sentences]
    longest_sentences = sorted(all_sentences, key=lambda s: s.word_count, reverse=True)[:5]
    hedge_examples = sorted(all_sentences, key=lambda s: s.hedge_count, reverse=True)[:5]
    passive_examples = [s for s in all_sentences if s.is_passive][:5]
    filler_examples = sorted(all_sentences, key=lambda s: s.filler_count, reverse=True)[:5]

    return DocumentMetrics(
        total_words=total_words,
        total_sentences=total_sentences,
        total_paragraphs=total_paragraphs,
        flesch_kincaid_grade=round(fk, 2),
        avg_sentence_length=round(avg_sl, 1),
        sentence_length_std=round(std_sl, 1),
        long_sentences=long_sents,
        very_long_sentences=very_long_sents,
        jargon_density=round(jargon_density, 2),
        passive_voice_pct=round(passive_pct, 1),
        hedge_density=round(hedge_d, 2),
        filler_density=round(filler_d, 2),
        filler_inventory=dict(sorted(filler_inv.items(), key=lambda x: -x[1])),
        hedge_inventory=dict(sorted(hedge_inv.items(), key=lambda x: -x[1])),
        weak_openers=weak_openers,
        sentence_length_cv=round(sl_cv, 3),
        monotony_score=round(mono, 3),
        short_sentence_pct=round(short_pct, 1),
        medium_sentence_pct=round(med_pct, 1),
        long_sentence_pct=round(long_pct, 1),
        avg_paragraph_length=round(avg_para_len, 1),
        paragraph_length_std=round(para_std, 1),
        sections=sec_metrics,
        opening_sentences=opening_sentences[:10],
        longest_sentences=[s.text for s in longest_sentences],
        hedge_examples=[s.text for s in hedge_examples],
        passive_examples=[s.text for s in passive_examples],
        filler_examples=[s.text for s in filler_examples],
        input_hash=input_hash,
        timestamp=ts,
    )


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _lerp(val: float, lo: float, hi: float, score_lo: float, score_hi: float) -> float:
    if hi == lo:
        return score_lo
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    return score_lo + t * (score_hi - score_lo)


def score_accessibility(m: DocumentMetrics) -> float:
    fk = m.flesch_kincaid_grade
    if fk <= 12:
        fk_s = 10.0
    elif fk <= 14:
        fk_s = _lerp(fk, 12, 14, 9, 10)
    elif fk <= 16:
        fk_s = _lerp(fk, 14, 16, 7, 9)
    elif fk <= 18:
        fk_s = _lerp(fk, 16, 18, 5, 7)
    elif fk <= 20:
        fk_s = _lerp(fk, 18, 20, 3, 5)
    else:
        fk_s = max(1.0, _lerp(fk, 20, 25, 1, 3))

    asl = m.avg_sentence_length
    if asl <= 15:
        asl_s = 10.0
    elif asl <= 25:
        asl_s = _lerp(asl, 15, 25, 9, 10)
    elif asl <= 35:
        asl_s = _lerp(asl, 25, 35, 6, 9)
    else:
        asl_s = max(1.0, _lerp(asl, 35, 50, 1, 6))

    lsp = m.long_sentences / max(1, m.total_sentences) * 100
    ls_s = max(1.0, 10.0 - lsp * 0.3)

    jd = m.jargon_density
    jd_s = max(1.0, 10.0 - jd * 1.5)

    return round((fk_s + asl_s + ls_s + jd_s) / 4, 2)


def score_clarity(m: DocumentMetrics) -> float:
    p = m.passive_voice_pct
    if p < 15:
        ps = 9.5
    elif p < 25:
        ps = _lerp(p, 15, 25, 7, 9.5)
    elif p < 35:
        ps = _lerp(p, 25, 35, 5, 7)
    elif p < 45:
        ps = _lerp(p, 35, 45, 3, 5)
    else:
        ps = max(1.0, _lerp(p, 45, 60, 1, 3))

    hd_s = max(1.0, 10.0 - m.hedge_density * 2.0)
    fd_s = max(1.0, 10.0 - m.filler_density * 3.0)
    wo_r = m.weak_openers / max(1, m.total_sentences)
    wo_s = max(1.0, 10.0 - wo_r * 30)

    return round((ps + hd_s + fd_s + wo_s) / 4, 2)


def score_flow(m: DocumentMetrics) -> float:
    cv = m.sentence_length_cv
    if 0.4 <= cv <= 0.6:
        cv_s = 9.5
    elif 0.3 <= cv < 0.4 or 0.6 < cv <= 0.7:
        cv_s = 7.5
    elif 0.2 <= cv < 0.3 or 0.7 < cv <= 0.8:
        cv_s = 5.5
    else:
        cv_s = 3.0

    mono_s = max(1.0, 10.0 - m.monotony_score * 12)

    # Balance penalty: ideal ~25/50/25
    s, med, lg = m.short_sentence_pct, m.medium_sentence_pct, m.long_sentence_pct
    balance_dev = (abs(s - 25) + abs(med - 50) + abs(lg - 25)) / 3
    bal_s = max(1.0, 10.0 - balance_dev * 0.15)

    pls = m.avg_paragraph_length
    if 80 <= pls <= 200:
        pl_s = 9.5
    elif 50 <= pls < 80 or 200 < pls <= 250:
        pl_s = 7.0
    else:
        pl_s = 4.0

    return round((cv_s + mono_s + bal_s + pl_s) / 4, 2)


def overall_grade(accessibility: float, clarity: float, flow: float) -> tuple:
    """Returns (numeric_score, letter_grade) using script-only dimensions."""
    score = (accessibility * 0.2 + clarity * 0.3 + flow * 0.2) / 0.7
    if score >= 9:
        letter = "A+"
    elif score >= 8:
        letter = "A"
    elif score >= 7:
        letter = "B+"
    elif score >= 6.5:
        letter = "B"
    elif score >= 5.5:
        letter = "B-"
    elif score >= 4.5:
        letter = "C+"
    elif score >= 4.0:
        letter = "C"
    elif score >= 3.0:
        letter = "D"
    else:
        letter = "F"
    return round(score, 1), letter


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _tick(val, target_ok: bool) -> str:
    return "+" if target_ok else "!"


def print_human(m: DocumentMetrics) -> None:
    acc = score_accessibility(m)
    cla = score_clarity(m)
    flo = score_flow(m)
    num, letter = overall_grade(acc, cla, flo)
    thr = SECTION_THRESHOLDS["_default"]

    print("=== Writing Quality Metrics ===")
    print(f"Words: {m.total_words:,} | Sentences: {m.total_sentences:,} | Paragraphs: {m.total_paragraphs:,}")
    print()
    print("ACCESSIBILITY")
    fk_lo, fk_hi = thr["fk_grade"]
    fk_ok = fk_lo <= m.flesch_kincaid_grade <= fk_hi
    asl_ok = 15 <= m.avg_sentence_length <= 25
    apl_ok = 80 <= m.avg_paragraph_length <= 200
    print(
        f"  Flesch-Kincaid grade:    {m.flesch_kincaid_grade:<6}"
        f"(target: {fk_lo}-{fk_hi}) {_tick(m.flesch_kincaid_grade, fk_ok)}"
    )
    print(
        f"  Avg sentence length:     {m.avg_sentence_length:<6}"
        f"(target: 15-25) {_tick(m.avg_sentence_length, asl_ok)}"
    )
    print(
        f"  Long sentences (>40w):   {m.long_sentences:<6}"
        f"(target: 0)     {_tick(m.long_sentences, m.long_sentences == 0)}"
    )
    print(
        f"  Jargon per paragraph:    {m.jargon_density:<6.1f}"
        f"(target: <4)    {_tick(m.jargon_density, m.jargon_density < 4)}"
    )
    print()
    print("CLARITY")
    print(
        f"  Passive voice:           {m.passive_voice_pct:.0f}%    "
        f"(target: <25%)  {_tick(m.passive_voice_pct, m.passive_voice_pct < 25)}"
    )
    print(
        f"  Hedge density:           {m.hedge_density:<6.1f}"
        f"(per 100 words) {_tick(m.hedge_density, m.hedge_density < 2)}"
    )
    print(
        f"  Filler density:          {m.filler_density:<6.1f}"
        f"(per 100 words) {_tick(m.filler_density, m.filler_density < 1)}"
    )
    print(
        f"  Weak openers:            {m.weak_openers:<6}"
        f"(target: 0)     {_tick(m.weak_openers, m.weak_openers == 0)}"
    )
    print()
    print("FLOW")
    print(
        f"  Sentence length CV:      {m.sentence_length_cv:<6.2f}"
        f"(target: >0.3)  {_tick(m.sentence_length_cv, m.sentence_length_cv > 0.3)}"
    )
    print(
        f"  Monotony score:          {m.monotony_score:<6.3f}"
        f"(target: <0.4)  {_tick(m.monotony_score, m.monotony_score < 0.4)}"
    )
    s_pct = m.short_sentence_pct
    med_pct = m.medium_sentence_pct
    lg_pct = m.long_sentence_pct
    print(f"  Short/Med/Long ratio:    {s_pct:.0f}/{med_pct:.0f}/{lg_pct:.0f}%")
    print(
        f"  Avg paragraph length:    {m.avg_paragraph_length:.0f}w    "
        f"(target: 80-200) {_tick(m.avg_paragraph_length, apl_ok)}"
    )
    print()
    print("SCORES")
    print(f"  Accessibility:           {acc}/10")
    print(f"  Clarity:                 {cla}/10")
    print(f"  Flow:                    {flo}/10")
    print(f"  Overall (script-only):   {letter} ({num})")


def _dc_to_dict(obj):
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _dc_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_dc_to_dict(i) for i in obj]
    return obj


class _DCEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return super().default(obj)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Compute writing quality metrics for scientific text.")
    parser.add_argument("input", help="Input file path or '-' for stdin")
    parser.add_argument("--format", choices=["latex", "markdown", "text", "auto"], default="auto")
    parser.add_argument("--section", help="Analyze only this section")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quick", action="store_true", help="Quick mode: global stats only")
    args = parser.parse_args()

    if args.input == "-":
        raw = sys.stdin.read()
        path = None
    else:
        with open(args.input, encoding="utf-8") as fh:
            raw = fh.read()
        path = args.input

    fmt = args.format if args.format != "auto" else detect_format(path, raw)

    if args.section:
        _, sections_raw = prepare_text(raw, fmt)
        key = args.section.lower().replace(" ", "_")
        matches = [k for k in sections_raw if key in k]
        if not matches:
            print(f"Section '{args.section}' not found. Available: {list(sections_raw.keys())}", file=sys.stderr)
            sys.exit(1)
        raw = sections_raw[matches[0]]
        fmt = "text"

    metrics = analyze_document(raw, fmt)

    if args.quick:
        if args.json:
            d = asdict(metrics)
            quick = {k: d[k] for k in (
                "total_words", "total_sentences", "total_paragraphs",
                "flesch_kincaid_grade", "avg_sentence_length", "passive_voice_pct",
                "hedge_density", "filler_density", "sentence_length_cv", "monotony_score",
            )}
            print(json.dumps(quick, indent=2))
        else:
            print_human(metrics)
        return

    if args.json:
        print(json.dumps(asdict(metrics), indent=2, cls=_DCEncoder))
    else:
        print_human(metrics)


if __name__ == "__main__":
    main()
