"""Safe FTS5 MATCH compilation for user free text.

Every user word becomes a double-quoted literal phrase term; embedded
double quotes are doubled per FTS5 syntax. FTS operators (OR/NEAR, column
filters, parentheses, asterisks, leading hyphens) can therefore never leak
through user input — normal words always behave as literal search terms.
Explicit structured operators come only from Alfred's own parser
(frontend searchParser + backend SearchFilters), never from raw text.

Parameterization is unchanged: the compiled string is still sent as a
single bound MATCH parameter, never concatenated into SQL.
"""


def compile_fts_match(words: list[str] | tuple[str, ...] | None) -> str | None:
    """Compile free-text words into a deterministic safe FTS5 MATCH string.

    Returns None when there are no usable terms (caller must use the LIKE
    fallback path instead of MATCH '', which is a syntax error).
    """
    if not words:
        return None
    terms: list[str] = []
    for word in words:
        text = (word or "").strip()
        if not text:
            continue
        # FTS5 escaping: a doubled quote inside a quoted term is a literal
        # double-quote character. Everything else stays literal.
        terms.append('"' + text.replace('"', '""') + '"')
    return " ".join(terms) or None
