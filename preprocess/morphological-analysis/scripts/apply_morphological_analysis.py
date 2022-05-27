import os
import io
import sys
import argparse
import json
import csv

from morphological_analyzer import MorphologicalAnalyzer


# for JSQuAD
# When title, question and context are tokenized, an answer_start position will be changed
def get_answer_start(tokenized_answer, context):
    answer = "".join(ch for ch in tokenized_answer if not ch.isspace())

    context_strip, offsets = zip(*[(ch, ptr) for ptr, ch in enumerate(context) if not ch.isspace()])
    idx = "".join(context_strip).index(answer)
    answer_start, answer_end = offsets[idx], offsets[idx + len(answer) - 1]
    tokenized_answer = context[answer_start:answer_end + 1]

    return tokenized_answer, answer_start


def process_squad_data(data, morphological_analyzer):
    # for each article
    for article in data:
        tokenized_title = morphological_analyzer.get_tokenized_string(article["title"])

        # for each paragraph
        for paragraph in article["paragraphs"]:
            title_context = paragraph["context"]
            _, context = title_context.split(" [SEP] ")
            tokenized_context = morphological_analyzer.get_tokenized_string(context)

            # for each qa
            for qa in paragraph["qas"]:
                tokenized_question = morphological_analyzer.get_tokenized_string(qa["question"])
                # for each answer
                for answer in qa["answers"]:
                    tokenized_answer = morphological_analyzer.get_tokenized_string(answer["text"])

                    try:
                        tokenized_answer, answer_start = get_answer_start(tokenized_answer,
                                                                          tokenized_title + " [SEP] " + tokenized_context)
                        answer["text"] = tokenized_answer
                        answer["answer_start"] = answer_start
                    except:
                        print(f"not found {answer} in {context}", file=sys.stderr)
                        continue
                qa["question"] = tokenized_question

            paragraph["context"] = f"{tokenized_title} [SEP] {tokenized_context}"

        article["title"] = tokenized_title

    return data


def main(args):
    morphological_analyzer = MorphologicalAnalyzer(args.morphological_analyzer,
                                                   mecab_dic_dir=args.mecab_dic_dir,
                                                   h2z=args.h2z)

    if args.input_file_type == "json":
        for line in sys.stdin:
            json_data = json.loads(line.rstrip("\n"))

            for column_name in args.column_names:
                string = json_data[column_name]
                tokenized_string = morphological_analyzer.get_tokenized_string(string)

                if tokenized_string is not None:
                    json_data[column_name] = tokenized_string
                else:
                    print(f"skip: parse error {json_data}", file=sys.stderr)
                    continue
            try:
                print(json.dumps(json_data, ensure_ascii=False))
            except:
                print(f"skip: {json_data}", file=sys.stderr)
                continue

    elif args.input_file_type == "csv":
        reader = csv.DictReader(sys.stdin)

        writer = csv.writer(sys.stdout)
        writer.writerow(reader.fieldnames)
        for row in reader:
            for column_name in args.column_names:
                string = row[column_name]
                tokenized_string = morphological_analyzer.get_tokenized_string(string)

                if tokenized_string is not None:
                    row[column_name] = tokenized_string
                else:
                    print(f"skip: tokenization error {json_data}", file=sys.stderr)
                    continue

            writer.writerow(row.values())

    elif args.input_file_type == "squad_json":
        data = None
        for line in sys.stdin:
            json_data = json.loads(line)
            data = json_data["data"]

        processed_data = process_squad_data(data, morphological_analyzer)
        print(json.dumps({"data": processed_data}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description="apply morphological analysis.")
    parser.add_argument("--morphological-analyzer",
                        choices=["jumanpp", "juman", "mecab", "char"],
                        default="jumanpp",
                        help="morphological analyzer (default: jumanpp)")
    parser.add_argument("--mecab-dic-dir",
                        type=str,
                        default=None,
                        help="dic dir for mecab")
    parser.add_argument("--input-file-type",
                        choices=["json", "csv", "squad_json"],
                        default="json")
    parser.add_argument("--column-names", nargs='*', default=[])
    parser.add_argument("--h2z",
                        action='store_true',
                        default=False,
                        help="hankaku to zenkaku")
    args = parser.parse_args()
    main(args)
