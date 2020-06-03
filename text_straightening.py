import re
from unidecode import unidecode


def straighten_punctuation(text):
    """
    Applies educated guesses to text punctuation to convert special unicode characters to their ASCII counterparts.
    Any alphanumeric characters are ignored.

    :param text: input string
    :return: string with punctuation converted to ASCII characters
    """
    
    # based on https://lexsrv3.nlm.nih.gov/LexSysGroup/Projects/lvg/current/docs/designDoc/UDF/unicode/DefaultTables/symbolTable.html
    unicode_symbols = ('\u00ab', '\u00ad', '\u00b4', '\u00bb', '\u00f7', '\u01c0', '\u01c3', '\u02b9', '\u02ba', '\u02bc', '\u02c4', '\u02c6', '\u02c8', '\u02cb', '\u02cd', '\u02dc', '\u0300', '\u0301', '\u0302', '\u0303', '\u030b', '\u030e', '\u0331', '\u0332', '\u0338', '\u0589', '\u05c0', '\u05c3', '\u066a', '\u066d', '\u200b', '\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2015', '\u2016', '\u2017', '\u2018', '\u2019', '\u201a', '\u201b', '\u201c', '\u201d', '\u201e', '\u201f', '\u2032', '\u2033', '\u2034', '\u2035', '\u2036', '\u2037', '\u2038', '\u2039', '\u203a', '\u203d', '\u2044', '\u204e', '\u2052', '\u2053', '\u2060', '\u20e5', '\u2212', '\u2215', '\u2216', '\u2217', '\u2223', '\u2236', '\u223c', '\u2264', '\u2265', '\u2266', '\u2267', '\u2303', '\u2329', '\u232a', '\u266f', '\u2731', '\u2758', '\u2762', '\u27e6', '\u27e8', '\u27e9', '\u2983', '\u2984', '\u3003', '\u3008', '\u3009', '\u301b', '\u301c', '\u301d', '\u301e', '\u301f', '\ufeff')
    ascii_symbols = ('"', '-', "'", '"', '/', '|', '!', "'", '"', "'", '^', '^', "'", '`', '_', '~', '`', "'", '^', '~', '"', '"', '_', '_', '/', ':', '|', ':', '%', '*', ' ', '-', '-', '--', '--', '--', '--', '||', '_', "'", "'", ',', "'", '"', '"', '"', '"', "'", '"', "'''", '`', '"', "'''", '^', '<', '>', '?', '/', '*', '%', '~', ' ', '\\', '-', '/', '\\', '*', '|', ':', '~', '<=', '>=', '<=', '>=', '^', '<', '>', '#', '*', '|', '!', '[', '<', '>', '{', '}', '"', '<', '>', ']', '~', '"', '"', '"', ' ')

    utf_to_ascii = {ord(ua[0]): ua[1] for ua in zip(unicode_symbols, ascii_symbols)}

    text = text.translate(utf_to_ascii)
    text = text.replace("--", "—")
    
    idxset = set()
    charlist = []
    for i, c in enumerate(text):
        if re.search(r"[^\w\s]", c):
            idxset.add(i)
            charlist.append(c)
    punct_mask = " ".join(charlist)
    punct_mask = unidecode(punct_mask)
    
    st_ch = iter(punct_mask.split(" "))
    straightened_text = "".join(next(st_ch) if i in idxset else c for i, c in enumerate(text))
    return straightened_text
