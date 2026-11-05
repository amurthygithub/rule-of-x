import re
# Supplement section numbers: build of 2-3 Nov (numbering used in response_to_outside_reviews.md) -> build of 4 Nov
SEC = {'4': '5', '5': '6', '6': '7', '7': '8', '8': '9', '9': '10'}
PRE = ('Remark', 'Remarks', 'Table', 'Tables', 'Figure', 'Lemma', 'Proposition', 'Corollary', 'Definition', 'Assumption', 'Equation', 'eq.')
PAT = re.compile(r'(?<![A-Za-z0-9])S(\d+)((?:\.\d+)*)(?![\d(])')

def convert(text):
    out, i = [], 0
    for m in PAT.finditer(text):
        before = text[max(0, m.start() - 14):m.start()]
        num, sub = m.group(1), m.group(2)
        if any(before.rstrip().endswith(p) for p in PRE) or re.search(r'(Remarks?|Tables?|Figures?|Lemmas?) S\d+[^.;)]*(and|to|,) $', before):
            continue
        if num in SEC:
            new = 'S' + SEC[num] + sub
        elif num == '10':
            new = 'S13' + sub if text[m.end():m.end() + 9].strip().startswith('glossary') else 'S11' + sub
        else:
            continue
        out.append(text[i:m.start()]); out.append(new); i = m.end()
    out.append(text[i:])
    return ''.join(out)
