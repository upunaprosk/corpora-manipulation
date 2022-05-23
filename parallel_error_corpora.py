import operator
import pandas as pd


def _rectify_patch(patch_list):
    """
    Sorts patch list and deals with overlapping patches (leaves only outer nested patch, also leaves the longest patch
    in case of otherwise overlapping patches, with the latest one being left in case of matching length).
    It also removes the patches in which the starting index is longer than the finishing.

    :param patch_list: list containing patches in [start, end, correction] notation
    :return: rectified patch list
    """
    patch_list.sort(key=operator.itemgetter(1))
    for i in reversed(range(len(patch_list) - 1)):
        start, end = patch_list[i][:2]
        corr = patch_list[i][-1]
        for j in range(i + 1, len(patch_list)):
            lstart, lend = patch_list[j][:2]
            lcorr = patch_list[j][-1]
            if lstart > lend:
                del patch_list[j]
                break
            if (start > lstart and end <= lend) or (start >= lstart and end < lend):
                del patch_list[i]
                break
            if (start == lstart and end == lend) or end > lstart:
                if len(corr) > len(lcorr):
                    del patch_list[j]
                else:
                    del patch_list[i]
                break
    return patch_list


def apply_patch_to_text(text, patch_list):
    """
    Applies correction to an individual text entry

    :param text: string containing original uncorrected text
    :param patch_list: list containing patches in [start, end, correction] notation
    :return: original text (str), corrected text (str), number of corrections (int)
    """
    l = len(text)
    patch_list = _rectify_patch(patch_list)
    corrections = len(patch_list)
    text_d = {i: c for i, c in enumerate(text)}

    for patch in patch_list:
        start, end = patch[:2]
        correction = patch[-1]
        if start == end:
            if start == l:
                text_d[start] = correction
            else:
                text_d[start] = correction + text_d[start]
        else:
            for i in range(start, end):
                text_d[i] = ""
            text_d[start] = correction

    corr_text = "".join([text_d[i] for i in range(len(text))])

    return text, corr_text, corrections


def list_to_corpus_df(list_notation):
    """
    Converts list notation to parallel corpus and returns a parallel corpus in form of a DataFrame/

    :param list_notation: a list of dicts, each containing "id" (entry id), "text" (original uncorrected text)
    and "patch" (list of corrections to the text)
    :return: pandas.DataFrame, containing columns id, orig_text, corr_text and corrections_num
    """

    df_dict = {
        "id": [],
        "orig_text": [],
        "corr_text": [],
        "corrections_num": []
    }

    for entry in list_notation:
        df_dict["id"].append(entry["id"])
        orig_text, corr_text, corrections_num = apply_patch_to_text(entry["text"], entry["patch"])
        df_dict["orig_text"].append(orig_text)
        df_dict["corr_text"].append(corr_text)
        df_dict["corrections_num"].append(corrections_num)

    parallel_corpus = pd.DataFrame(df_dict)
    parallel_corpus.columns = ["id", "orig_text", "corr_text", "corrections_num"]

    return parallel_corpus


def list_to_corpus_df_realec(list_notation):
    """
    Converts list notation to parallel corpus, performs some additional REALEC-specific cleanup
    and returns a parallel corpus in form of a DataFrame.

    :param list_notation: a list of dicts, each containing "id" (entry id), "text" (original uncorrected text)
    and "patch" (list of corrections to the text)
    :return: pandas.DataFrame, containing columns id, orig_text, corr_text and corrections_num
    """
    
    
    import re
    from text_straightening import straighten_punctuation
       
    df_dict = {
        "id": [],
        "orig_text": [],
        "corr_text": [],
        "corrections_num": []
    }
    
    for entry in list_notation:
        try:
            new_patch = []
            for el in entry["patch"]:
                if el[0]:
                    if re.search(r"[^\W\d_]", entry["text"][el[0] - 1]) and re.search(r"\w", el[2]):
                        el[1] -= 1
                        el[2] = entry["text"][el[0]:el[1] - 1] + el[2]
                new_patch.append(el)
            
            orig_text, corr_text, corrections_num = apply_patch_to_text(entry["text"], new_patch)
            
            corr_text = straighten_punctuation(corr_text)  # replace all non-standard characters except em dash (—)
            # trim every repeating punctuation mark, except dot, to its first occurrence:
            corr_text = re.sub(r'(([^\w\.])\2+)', r'\g<2>', corr_text)
        
        except Exception as e:
            print("Failed at", entry["id"], "with", str(e))
            continue
        
        df_dict["id"].append(entry["id"])
        df_dict["orig_text"].append(orig_text)
        df_dict["corr_text"].append(corr_text)
        df_dict["corrections_num"].append(corrections_num)
    
    parallel_corpus = pd.DataFrame(df_dict)
    parallel_corpus.columns = ["id", "orig_text", "corr_text", "corrections_num"]
    
    return parallel_corpus
