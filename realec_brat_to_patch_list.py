import re
from collections import OrderedDict


class AnnEntry:
    def __new__(cls, ann_line):
        line = ann_line.split("\t")
        line[1] = _ann_demultiplify(line[1])
        line = [line[0]] + line[1].split(" ") + line[2:]
        return line


class TextPatch:
    def __init__(self, ann_entry):
        self.start = int(ann_entry[2])
        self.end = int(ann_entry[3])
        self.err_type = ann_entry[1]
        self.orig_str = None
        self.corr_str = None
        self.name = ann_entry[0]
        if self.name[0] == "T":
            self.orig_str = ann_entry[4]


def _ann_demultiplify(ann_line):
    """
    Converts stacked annotation entries to one single entry with previous entries' spans combined as well as
    including the portions of string within it.
    """

    return re.sub(r"([0-9]+).*( [0-9]+)", "\g<1>\g<2>", ann_line)


def _check_entry(ann_entry):
    """
    Checks if the line in annotation file is not corrupted and should contribute to the parallel corpus.
    """
    if not ann_entry:
        return False

    if ann_entry[0] == "#":
        if re.search(r"^#[0-9]+\tAnnotatorNotes T[0-9]+\t.*?$", ann_entry):
            return True
        return False

    if ann_entry[0] == "A":
        if re.search(r"^A[0-9]+\tDelete T[0-9]+$", ann_entry):
            return True
        return False

    allowed_errors = "(" + "|".join(("Punctuation", "Spelling", "Capitalisation", "Grammar", "Determiners", "Articles",
                                     "Quantifiers", "Verbs", "Tense", "Tense_choice", "Tense_form", "Voice", "Modals",
                                     "Verb_pattern", "Intransitive", "Transitive", "Reflexive_verb", "Presentation",
                                     "Ambitransitive", "Two_in_a_row", "Verb_Inf", "Verb_Gerund", "Verb_Inf_Gerund",
                                     "Verb_Bare_Inf", "Verb_object_bare", "Restoration_alter", "Verb_part", "Get_part",
                                     "Complex_obj", "Verbal_idiom", "Prepositional_verb", "Dative",
                                     "Followed_by_a_clause", "that_clause", "if_whether_clause", "that_subj_clause",
                                     "it_conj_clause", "Participial_constr", "Infinitive_constr", "Gerund_phrase",
                                     "Nouns", "Countable_uncountable", "Prepositional_noun", "Possessive",
                                     "Noun_attribute", "Noun_inf", "Noun_number", "Prepositions", "Conjunctions",
                                     "Adjectives", "Comparative_adj", "Superlative_adj", "Prepositional_adjective",
                                     "Adj_as_collective", "Adverbs", "Comparative_adv", "Superlative_adv",
                                     "Prepositional_adv", "Numerals", "Pronouns", "Agreement_errors", "Word_order",
                                     "Standard", "Emphatic", "Cleft", "Interrogative", "Abs_comp_clause", "Exclamation",
                                     "Title_structure", "Note_structure", "Conditionals", "Attributes",
                                     "Relative_clause", "Defining", "Non_defining", "Coordinate", "Attr_participial",
                                     "Lack_par_constr", "Negation", "Comparative_constr", "Numerical",
                                     "Confusion_of_structures", "Vocabulary", "Word_choice", "lex_item_choice",
                                     "Often_confused", "lex_part_choice", "Absence_comp_colloc", "Redundant",
                                     "Derivation", "Formational_affixes", "Suffix", "Prefix", "Category_confusion",
                                     "Compound_word", "Discourse", "Ref_device", "Coherence", "Linking_device",
                                     "Inappropriate_register", "Absence_comp_sent", "Redundant_comp",
                                     "Absence_explanation")) + ")"

    if ann_entry[0] == "T":
        if re.search(r"^T[0-9]+\t" + allowed_errors + " [0-9]+ [0-9]+\t.*?$", ann_entry):
            return True
        return False
    return False


def endswithpunct(instr):
    """
    Checks if a string ends with a sequence of punctuation marks. If so, returns this sequence.
    Else, returns an empty string
    """

    sr = re.search(r"\W+$", instr)
    if sr:
        return sr.group(0)
    else:
        return ""


def rectify_patch(patch_dict):
    """
    Performs a part of annotation cleaning routine. Ignores annotation without correction suggestions
    (with delete suggestions already accounted) and adds missed punctuation in case the correction wrongly omitted it.
    """

    rectified_list = []
    pd = patch_dict
    textpatch_list = sorted(pd.items(), key=lambda k: (k[1].start, k[1].end, int(k[0][1:])))
    for el in textpatch_list:
        patch = el[1]
        if patch.corr_str is None:  # ignores annotations without correction suggestions
            continue
        p = endswithpunct(patch.orig_str)
        if p:
            if not endswithpunct(patch.corr_str) and patch.corr_str != "":  # to not add back what we want to delete
                patch.corr_str += p  # adds punctuation in case correction suggestion omits it
        rectified_list.append(patch)
    return rectified_list


def textpatch_to_patchlist(patch_list):
    fix_list = []
    for patch in patch_list:
        fix_list.append([patch.start, patch.end, patch.corr_str])
    return fix_list


def ann_to_patchlist(ann_file):
    with open(ann_file, "r", encoding="utf-8") as inann:
        ann_lines = sorted([al for al in inann.read().split("\n") if _check_entry(al)], reverse=True)
    ann_lines = [AnnEntry(line) for line in ann_lines]
    patch_dict = OrderedDict()
    for entry in ann_lines:
        if entry[0][0] == "T":
            tp = TextPatch(entry)
            patch_dict[tp.name] = tp
        elif entry[0][0] == "#":
            if entry[2] in patch_dict:
                patch_dict[entry[2]].corr_str = entry[3]
        elif entry[0][0] == "A" and entry[1] == "Delete":
            if entry[2] in patch_dict:
                patch_dict[entry[2]].corr_str = ""
        else:
            pass
    patch_list = rectify_patch(patch_dict)
    fix_list = textpatch_to_patchlist(patch_list)
    return fix_list
