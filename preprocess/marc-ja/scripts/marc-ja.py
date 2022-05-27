import os
import io
import sys
import argparse
import json
import csv
import string
import random
from collections import defaultdict
from bs4 import BeautifulSoup

import zenhan

csv.field_size_limit(1000000)


def is_filtered_by_ascii_rate(text, threshold=0.9):
    ascii_letters = set(string.printable)
    rate = sum(c in ascii_letters for c in text) / len(text)
    return rate >= threshold


def get_label(rating,
              positive_negative=False):
    label = None

    if rating >= 4:
        label = "positive"
    elif rating <= 2:
        label = "negative"
    else:
        if positive_negative is True:
            return None
        label = "neutral"

    return label


def get_filter_review_id_list(args):
    filter_review_id_list = defaultdict(list)

    if args.filter_review_id_list_valid is not None:
        with open(args.filter_review_id_list_valid, "r") as f:
            filter_review_id_list["valid"] = [line.rstrip() for line in f]

    if args.filter_review_id_list_test is not None:
        with open(args.filter_review_id_list_test, "r") as f:
            filter_review_id_list["test"] = [line.rstrip() for line in f]

    return filter_review_id_list


def get_label_conv_review_id_list(args):
    label_conv_review_id_list = defaultdict(list)

    if args.label_conv_review_id_list_valid is not None:
        with open(args.label_conv_review_id_list_valid, "r") as f:
            label_conv_review_id_list["valid"] = {row[0]: row[1] for row in csv.reader(f)}

    if args.label_conv_review_id_list_test is not None:
        with open(args.label_conv_review_id_list_test, "r") as f:
            label_conv_review_id_list["test"] = {row[0]: row[1] for row in csv.reader(f)}

    return label_conv_review_id_list


def output_data(instances, args):
    os.makedirs(args.output_dir, exist_ok=True)

    instance_num = len(instances)

    splitted_instances = {}

    length1 = int(instance_num * args.split_ratio[0])
    splitted_instances["train"] = instances[:length1]

    length2 = int(instance_num * (args.split_ratio[0] + args.split_ratio[1]))
    splitted_instances["valid"] = instances[length1:length2]
    splitted_instances["test"] = instances[length2:]

    filter_review_id_list = get_filter_review_id_list(args)
    label_conv_review_id_list = get_label_conv_review_id_list(args)

    for eval_type in ("train", "valid", "test"):
        if args.output_testset is False and eval_type == "test":
            continue

        out_file = os.path.join(args.output_dir, "{}-v{}.json".format(eval_type, args.version))
        with open(out_file, mode="w") as f:
            for instance in splitted_instances[eval_type]:
                # filter
                if len(filter_review_id_list) != 0:
                    filter_flag = False
                    for filter_eval_type in ("valid", "test"):
                        if eval_type == filter_eval_type and instance["review_id"] in filter_review_id_list[filter_eval_type]:
                            filter_flag = True
                        if eval_type != filter_eval_type:
                            if filter_eval_type in filter_review_id_list:
                                assert instance["review_id"] not in filter_review_id_list[filter_eval_type]

                    if filter_flag is True:
                        continue

                # convert labels
                if len(label_conv_review_id_list) != 0:
                    for conv_eval_type in ("valid", "test"):
                        if eval_type == conv_eval_type and instance["review_id"] in label_conv_review_id_list[conv_eval_type]:
                            assert instance["label"] != label_conv_review_id_list[conv_eval_type][instance["review_id"]]
                            # update
                            instance["label"] = label_conv_review_id_list[conv_eval_type][instance["review_id"]]

                        if eval_type != conv_eval_type:
                            if conv_eval_type in label_conv_review_id_list:
                                assert instance["review_id"] not in label_conv_review_id_list[conv_eval_type]

                if eval_type == "test":
                    del instance["label"]

                print(json.dumps(instance, ensure_ascii=False), file=f)


def main(args):
    reader = csv.reader(sys.stdin, delimiter="\t")
    next(reader)

    instances = []
    instance_num = 0
    for row in reader:
        text = row[13]
        rating = int(row[7])
        review_id = row[2]
        label = get_label(rating,
                          positive_negative=args.positive_negative)
        if label is None:
            continue

        text = BeautifulSoup(text, "html.parser").get_text()
        if is_filtered_by_ascii_rate(text):
            continue
        if args.max_char_length is not None and len(text) > args.max_char_length:
            continue

        if args.h2z is True:
            text = zenhan.h2z(text)

        instances.append(dict(sentence=text, label=label, review_id=review_id))
        instance_num += 1

        if args.max_instance_num is not None:
            if instance_num == args.max_instance_num:
                break

    random.seed(1)
    random.shuffle(instances)

    output_data(instances, args)


if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description="preprocess an amazon review.")
    parser.add_argument("--output-dir", type=str, required=True, default=None, help="output dir")
    parser.add_argument("--version", type=float, default=1.0, help="dataset version")
    parser.add_argument("--h2z", action='store_true', default=False, help="hankaku to zenkaku")
    parser.add_argument("--max-instance-num", type=int, default=None, help="max instance num")
    parser.add_argument("--max-char-length", type=int, default=None, help="max char length")
    parser.add_argument("--positive-negative", action='store_true', default=False, help="discard neutral")
    parser.add_argument("--split-ratio", nargs='*', default=[0.94, 0.03, 0.03], help='split ratio')
    parser.add_argument("--output-testset", action='store_true', default=False, help="output testset")
    parser.add_argument("--filter-review-id-list-valid", type=str, default=None, help="filter review id list for validation set")
    parser.add_argument("--filter-review-id-list-test", type=str, default=None, help="filter review id list for test set")
    parser.add_argument("--label-conv-review-id-list-valid", type=str, default=None, help="label conv review id list for validation set")
    parser.add_argument("--label-conv-review-id-list-test", type=str, default=None, help="label conv review id list for test set")

    args = parser.parse_args()
    args.split_ratio = [float(f) for f in args.split_ratio]
    assert sum(args.split_ratio) == 1.0

    main(args)
