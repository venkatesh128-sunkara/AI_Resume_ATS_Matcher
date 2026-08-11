import re
import string

STOPWORDS = set(
    """
a an and are as at be by for from has have in is it its of on or that the this
to was were will with i you we they he she we'll would could should may might
must can shall our your their my his her its our's yours theirs about above after
again against all am any because been before being below between both but cannot
do does did doing down during each few further get had he'd he's here how if into
just more most no nor not now off once only other out over own same so some such
than then there these those through under until up very what when where which who
whom why why's too also etc ie eg us them him it's
""".split()
)

PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def tokenize(text: str):
    return re.findall(r"[a-zA-Z][a-zA-Z0-9.+#]*", text.lower())


def clean_tokens(text: str):
    return [t for t in tokenize(text) if t not in STOPWORDS and len(t) > 1]


def phrases(text: str, max_n: int = 3):
    tokens = clean_tokens(text)
    result = set(tokens)
    for n in range(2, max_n + 1):
        for i in range(len(tokens) - n + 1):
            result.add(" ".join(tokens[i : i + n]))
    return result


def sentence_aware_phrases(text: str, max_n: int = 3):
    result = set()
    sentences = re.split(r"[.!?;:]+", text.lower())
    for sentence in sentences:
        tokens = clean_tokens(sentence)
        if not tokens:
            continue
        result.update(tokens)
        for n in range(2, max_n + 1):
            for i in range(len(tokens) - n + 1):
                result.add(" ".join(tokens[i : i + n]))
    return result


def pos_noun_phrases(text: str):
    """Extract noun phrases via NLTK POS chunking. Falls back to simple n-grams
    if NLTK resources are unavailable."""
    try:
        from nltk import word_tokenize, pos_tag
        from nltk.chunk import RegexpParser
    except Exception:
        return sorted(sentence_aware_phrases(text, 2))

    cp = RegexpParser("NP: {<JJ.*>*<NN.*>+}")
    phrases_out = []
    for sent in re.split(r"[.!?;:]+", text):
        sent = sent.strip()
        if not sent:
            continue
        try:
            tokens = word_tokenize(sent.lower())
            if not tokens:
                continue
            tree = cp.parse(pos_tag(tokens))
            for subtree in tree.subtrees():
                if subtree.label() == "NP":
                    words = [w for w, _tag in subtree.leaves()]
                    if words:
                        phrases_out.append(" ".join(words))
        except Exception:
            continue
    return phrases_out


def find_skill_mentions(text: str, skills):
    lowered = text.lower()
    mentions = [s for s in skills if re.search(r"(^|[\s\W])" + re.escape(s) + r"([\s\W]|$)", lowered)]
    return mentions
