import sys
import io
import os
import argparse
import json
import csv


def get_input_string(input_data, task_type, additional_column_name_string):
    input_strings = []
    if additional_column_name_string is not None:
        for additional_column_name in additional_column_name_string.split(","):
            input_strings.append(str(input_data[additional_column_name]))

    if task_type == "single-sentence":
        input_strings.append(input_data["sentence"])
    elif task_type == "sentence-pair":
        input_strings.extend([input_data["sentence1"], input_data["sentence2"]])
    elif task_type == "swag":
        input_strings.extend([str(input_data["question"]),
                              input_data["choice0"], input_data["choice1"], input_data["choice2"],
                              input_data["choice3"], input_data["choice4"]])

    return "\t".join(input_strings)


def get_eval_string(input_data, system_predict,
                    classification_type, task_type):
    if classification_type == "regression":
        return "{:.3f}".format(abs(float(system_predict) - float(input_data["label"])))
    elif classification_type == "classification":
        if task_type == "swag":
            return "CORRECT" if int(system_predict) == input_data["label"] else "WRONG"
        else:
            return "CORRECT" if system_predict == str(input_data["label"]) else "WRONG"


def print_header(args):
    columns = []
    if args.additional_column_name_string is not None:
        columns.extend(args.additional_column_name_string.split(","))
    if args.task_type == "single-sentence":
        columns.append("sentence")
    elif args.task_type == "sentence-pair":
        columns.extend(["sentence1", "sentence2"])
    elif args.task_type == "swag":
        columns.extend(["question", "choice0", "choice1", "choice2", "choice3", "choice4"])

    columns.append("system")
    columns.append("gold")
    columns.append("eval")

    print("\t".join(columns))


def main(args):
    print_header(args)

    with open(args.system_predict_txt, "r", encoding="utf-8") as system_f:
        next(system_f)

        with open(args.input_file, "r", encoding="utf-8") as input_f:
            for row_system_predict, input in zip(csv.reader(system_f, delimiter="\t"),
                                                 input_f.readlines() if args.input_file_type == "json"
                                                 else csv.DictReader(input_f)):
                input_data = None
                if args.input_file_type == "json":
                    input_data = json.loads(input)
                else:
                    input_data = input

                system_predict = row_system_predict[1]

                input_string = get_input_string(input_data, args.task_type,
                                                args.additional_column_name_string)
                eval_string = get_eval_string(input_data, system_predict,
                                              args.classification_type, args.task_type)
                # input  system  goal evaluation
                print("{}\t{}\t{}\t{}".format(input_string,
                                              system_predict,
                                              input_data["label"],
                                              eval_string
                                              ))


if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description="print system result")
    parser.add_argument("--system-predict-txt", type=str, default=None, required=True, help="system prediction file")
    parser.add_argument("--input-file", type=str, default=None, required=True, help="input file")
    parser.add_argument("--input-file-type", choices=["json", "csv"], default="json")
    parser.add_argument("--task-type", choices=["single-sentence", "sentence-pair", "swag"], default="single-sentence")
    parser.add_argument("--classification-type", choices=["classification", "regression"], default="classification")
    parser.add_argument("--additional-column-name-string", type=str, default=None, help="additional column name string (comma separated)")
    args = parser.parse_args()

    main(args)
