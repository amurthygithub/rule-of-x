"""Registrants excluded from every universe, panel and data file of this repository.

A registrant is identified by the SHA-256 digest (hex) of its SEC CIK written as a decimal string without leading zeros,
so this file does not name it. Every script that fetches or builds a universe or a panel drops the registrants whose
digest is in EXCLUDED_CIK_SHA256 (code/fetch_companyfacts.py, code/retrieval_browser.js, code/growth_from_filings.py,
code/build_panel*.py, code/data_part2/05, 08 and 11, code/validation/backtest.py, code/make_arxiv.py,
code/extract_browser_payload.py); code/purge_excluded.py removes them from the data files already on disk and checks
that none is left. code/retrieval_browser.js carries a copy of the digest set, which `purge_excluded.py --check` compares
with this one.
"""
import hashlib
import numbers

# registrant excluded at the author's request
EXCLUDED_CIK_SHA256 = frozenset({
    '98a09ebecd587b52c233f1dda385c92194cf862e9caf6d436716baddf1c022f3',
})


def cik_digest(cik):
    """SHA-256 hex digest of a CIK given as an integer, an integral float or a decimal string (zero-padded or not)."""
    if isinstance(cik, numbers.Integral) and not isinstance(cik, bool):
        s = str(int(cik))
    elif isinstance(cik, numbers.Real) and not isinstance(cik, bool):
        if not float(cik).is_integer():
            raise ValueError(cik)
        s = str(int(cik))
    else:
        s = str(int(str(cik).strip()))
    return hashlib.sha256(s.encode()).hexdigest()


def is_excluded(cik):
    """True when the registrant is excluded. Values that are not a decimal CIK are never excluded."""
    try:
        return cik_digest(cik) in EXCLUDED_CIK_SHA256
    except (TypeError, ValueError):
        return False


def drop_excluded(df, col='cik'):
    """A pandas DataFrame without the rows of excluded registrants (column `col` holds the CIK)."""
    return df[~df[col].map(is_excluded)]
