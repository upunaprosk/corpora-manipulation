import spacy
from spacy.language import Language


@Language.component("sentencizer_boundaries")
def set_custom_boundaries(doc):
    quotes = {"\'", "’", "\""}
    for token in doc[:-1]:
        if token.text in {"’s", "'s", "\"s"} or token.text in quotes:
            doc[token.i].is_sent_start = False
        if token.text in {".", "!", "?"} and doc[token.i + 1].text in quotes:
            doc[token.i].is_sent_start = False
    return doc


def sentencize_patch(nlp, text, errors):
    doc = nlp(text)
    def check_error_span(error_start, error_end):
        if error_start > error_end:
            return False
        return True
    error_i = 0
    sents, errs = [], []
    for doc in doc.sents:
        start, end = doc.start_char, doc.end_char
        err_l = []
        while error_i < len(errors) and check_error_span(errors[error_i][0], end):
            ee_i = errors[error_i][:3]
            ee_i[0] -= start
            ee_i[1] -= start
            ee_i[-1] = errors[error_i][-1]
            err_l.append(ee_i)
            error_i += 1
        if err_l:
            sents.append(doc.text)
            errs.append(err_l)
    return dict(zip(sents, errs))