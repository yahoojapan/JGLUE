import os
import io
import sys
import argparse
import json
import subprocess


def main(args):
    datasets = json.load(open(args.datasets_json))
    for dataset in datasets:
        input_dir = f"{args.data_dir}/{dataset['dirname']}"
        for morphological_analyzer in args.morphological_analyzers:
            output_dir = f"{args.data_dir}/{dataset['dirname']}_{morphological_analyzer}"

            target = dataset["target"] if "target" in dataset else "out_train_file out_valid_file out_test_file"
            cmds = ["make", target,
                    "-f", "Makefile",
                    "INPUT_DIR={}".format(input_dir),
                    "OUTPUT_DIR={}".format(output_dir),
                    "TRAIN_FILE_BASENAME={}".format(dataset["train_file_basename"]),
                    "VALID_FILE_BASENAME={}".format(dataset["valid_file_basename"]),
                    "TEST_FILE_BASENAME={}".format(dataset["test_file_basename"]),
                    "MORPHOLOGICAL_ANALYZER={}".format(morphological_analyzer),
                    "INPUT_FILE_TYPE={}".format(dataset["input-file-type"])]
            if "column-names" in dataset:
                cmds.append("COLUMN_NAMES=\"{}\"".format(dataset["column-names"]))
            if "test_file_basename" in dataset:
                cmds.append("TEST_FILE_BASENAME={}".format(dataset["test_file_basename"]))
            if args.h2z is True:
                cmds.append("H2Z=1")
            if "mecab" in morphological_analyzer and args.mecab_dic_dir is not None:
                cmds.append("MECAB_DIC_DIR={}".format(args.mecab_dic_dir))

            if args.dry_run is True:
                cmds.insert(1, "-n")

            cmd = ' '.join(cmds)
            completed = subprocess.run(cmd, shell=True)
            print(completed, file=sys.stderr)


if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors="surrogateescape")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description="apply morphological analysis to all the datasets.")
    parser.add_argument("--datasets-json",
                        type=str,
                        default=None,
                        required=True,
                        help="json for datasets")
    parser.add_argument("--data-dir",
                        type=str,
                        default=None,
                        help="data dir")
    parser.add_argument("--dry-run", help='dry run', action='store_true')
    parser.add_argument("--morphological-analyzers",
                        nargs="*",
                        default=["jumanpp", "mecab"],
                        help='morphological analyzers')
    parser.add_argument("--mecab-dic-dir",
                        type=str,
                        default=None,
                        help="dic dir for mecab")
    parser.add_argument("--h2z",
                        action='store_true',
                        default=False,
                        help="hankaku to zenkaku")
    args = parser.parse_args()
    main(args)
