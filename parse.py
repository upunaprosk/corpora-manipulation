import argparse
from parallel_error_corpora import *
from realec_brat_to_patch_list import *
from realec_patch_sentencize import *


def main(args):

    all_ann_files = glob.glob(f'{args.input_dir}/**/*.ann', recursive=True)
    error = args.error_type
    realec_entries = []
    textpatch_format = False
    if error: textpatch_format = True;
    for path in tqdm(all_ann_files):
        fid = path[:-3] + "txt"
        essay_id = path[:-3].split("\\")[-1][:-1]
        try:
            patch = ann_to_patchlist(path, textpatch_format=textpatch_format)
            if patch:
                with open(fid, "r", encoding="utf-8") as intxt:
                    text = intxt.read()
                    if error:
                        text, patch = filter_patch(text, patch, error)
                    if not patch: continue
                    if args.sentencize:
                        nlp = spacy.load('en_core_web_sm', disable=['ner', 'attribute_ruler', 'lemmatizer'])
                        nlp.add_pipe('sentencizer_boundaries', before="parser")
                        upd = sentencize_patch(nlp, text, patch)
                        for key, value in upd.items():
                            realec_entries.append({"id": essay_id,
                                                   "text": key,
                                                   "patch": value})
                    else:
                        realec_entries.append({"id": essay_id,
                                               "text": text,
                                               "patch": patch})
        except:
            print(f"File does not exist: {fid}")
    if realec_entries:
        realec_df = list_to_corpus_df_realec(realec_entries)
        if error:
            realec_df = realec_df.drop(["corrections_num"], axis=1)
        realec_df = realec_df.sort_values(by=['id']).reset_index(drop=True)
        filename = "realec_df"
        if error:
            filename += f"_{error}"
        os.makedirs(f"{args.output_dir}", exist_ok=True)
        realec_df.to_pickle(f"{args.output_dir}/{filename}.pickle")
    else:
        print("No erroneous entites found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse parallel data"
    )
    parser.add_argument("-error_type", type=str, default="", help='error_type')
    parser.add_argument("--sentencize", action=argparse.BooleanOptionalAction)
    parser.add_argument("--input_dir", type=str, default="realec_data",
                              help = "Input directory (default: %(default)s)")
    parser.add_argument("--output_dir", type=str, default="realec_parallel",
                              help = "Output directory (default: %(default)s)")
    args = parser.parse_args()
    main(args)
