# Fine-tuning

We used [the transformers library](https://github.com/huggingface/transformers) for our fine-tuning experiments, and modified the original codes to fit our datasets and experimental settings. We used v4.9.2, but other versions may work (we have confirmed that v4.19.2, the latest version as of June 2022, worked).

```bash
# This directory is for installing transformers. This directory would be better outside the JGLUE repository.)
$ cd /somewhere/  
$ git clone https://github.com/huggingface/transformers.git -b v4.9.2 transformers-4.9.2
$ cd transformers-4.9.2
$ patch -p1 < /somewhere2/JGLUE/fine-tuning/patch/transformers-4.9.2_jglue-1.1.0.patch
$ pip install .
$ pip install -r examples/pytorch/text-classification/requirements.txt
$ pip install protobuf==3.19.1 tensorboard
# For the cl-tohoku/bert-base-japanese-v2 model
$ pip install fugashi unidic-lite
```

## Hyperparameters

The following table lists hyperparameters used in our experiments. The numbers in curly brackets represent the range of possible values. The best hyperparameters were searched using the dev set.

|Name|Value(s)|
|----|-------|
|learning rate|{5e-5, 3e-5, 2e-5}|
|epoch|{3, 4}|
|warmup ratio|0.1|
|max seq length|512 (MARC-ja), 128 (JSTS, JNLI), 384 (JSQuAD), 64 (JCommonsenseQA)|

## Text classification and sentence pair classification tasks

This section is for `MARC-ja`, `JSTS` and `JNLI`. When you fine-tune the `cl-tohoku/bert-base-japanese-v2` model for the `MARC-ja` dataset, run the following command:

```bash
$ export OUTPUT_DIR=/path/to/output_marc
$ python /somewhere/transformers-4.9.2/examples/pytorch/text-classification/run_glue.py \
     --model_name_or_path cl-tohoku/bert-base-japanese-v2 \
     --metric_name sst2 \
     --do_train --do_eval --do_predict \
     --max_seq_length 512 \
     --per_device_train_batch_size 32 \
     --learning_rate 5e-05 \
     --num_train_epochs 4 \
     --output_dir $OUTPUT_DIR \
     --train_file ../datasets/marc_ja-v1.1/train-v1.1.json \
     --validation_file ../datasets/marc_ja-v1.1/valid-v1.1.json \
     --test_file ../datasets/marc_ja-v1.1/valid-v1.1.json \
     --use_fast_tokenizer False \
     --evaluation_strategy epoch \
     --save_steps 5000 \
     --warmup_ratio 0.1
```

`--metric_name` option should be set according to a dataset as follows:
- MARC-ja: sst2
- JSTS: stsb
- JNLI: wnli

When you fine-tune the NICT BERT base or Waseda RoBERTa base/large models, please specify the word-segmented files with `--train_file`, `--validation_file` and `--test_file` options (see [preprocess/morphological-analysis/README.md](/preprocess/morphological-analysis/README.md) for how to perform word segmentation). For example, you use Waseda RoBERTa base/large models, these options are as follows:

```bash
     ..
     --train_file ../datasets/marc_ja-v1.1_jumanpp/train-v1.1.json \
     --validation_file ../datasets/marc_ja-v1.1_jumanpp/valid-v1.1.json \
     -test_file ../datasets/marc_ja-v1.1_jumanpp/valid-v1.1.json \
     ..  
```

The system prediction for the validation set is output to `$OUTPUT_DIR/predict_results_${metric_name}.txt`.
For the examination of the system prediction, the system prediction as well as the evaluation result can be output as follows:

- MARC-ja
```bash
$ python scripts/generate_results.py \
     --system-predict-txt $OUTPUT_DIR/predict_results_sst2.txt \
     --input-file ../datasets/marc_ja-v1.1/valid-v1.1.json \
     --task-type single-sentence \
     --additional-column-name-string review_id > $OUTPUT_DIR/predict_eval_results.tsv
```
- JSTS
```bash
$ python scripts/generate_results.py \
     --system-predict-txt $OUTPUT_DIR/predict_results_stsb.txt \
     --input-file ../datasets/jsts-v1.1/valid-v1.1.json \
     --task-type sentence-pair \
     --classification-type regression \
     --additional-column-name-string sentence_pair_id,yjcaptions_id > $OUTPUT_DIR/predict_eval_results.tsv
```

- JNLI
```bash 
$ python scripts/generate_results.py \
     --system-predict-txt $OUTPUT_DIR/predict_results_wnli.txt \
     --input-file ../datasets/jnli-v1.1/valid-v1.1.json \
     --task-type sentence-pair \
     --additional-column-name-string sentence_pair_id,yjcaptions_id > $OUTPUT_DIR/predict_eval_results.tsv
``` 
## QA: JSQuAD

```
$ export OUTPUT_DIR=/path/to/output_jsquad
$ python /somewhere/transformers-4.9.2/examples/legacy/question-answering/run_squad.py \
     --model_type bert \
     --model_name_or_path cl-tohoku/bert-base-japanese-v2 \
     --do_train --do_eval \
     --max_seq_length 384 \
     --learning_rate 5e-05 \
     --num_train_epochs 3 \
     --per_gpu_train_batch_size 32 \
     --per_gpu_eval_batch_size 32 \
     --output_dir $OUTPUT_DIR \
     --train_file ../datasets/jsquad-v1.1/train-v1.1.json \
     --predict_file ../datasets/jsquad-v1.1/valid-v1.1.json \
     --save_steps 5000 \
     --warmup_ratio 0.1 \
     --evaluate_prefix eval
```

## QA: JCommonsenseQA

```bash
$ export OUTPUT_DIR=/path/to/output_jcommonsenseqa
$ python /somewhere/transformers-4.9.2/examples/pytorch/multiple-choice/run_swag.py \
     --model_name_or_path cl-tohoku/bert-base-japanese-v2 \
     --do_train --do_eval --do_predict \
     --max_seq_length 64 \
     --per_device_train_batch_size 64 \
     --learning_rate 5e-05 \
     --num_train_epochs 4 \
     --output_dir $OUTPUT_DIR \
     --train_file ../datasets/jcommonsenseqa-v1.1/train-v1.1.json \
     --validation_file ../datasets/jcommonsenseqa-v1.1/valid-v1.1.json \
     --test_file ../datasets/jcommonsenseqa-v1.1/valid-v1.1.json \
     --use_fast_tokenizer False \
     --evaluation_strategy epoch \
     --warmup_ratio 0.1
```

For the examination of the system prediction, the system prediction as well as the evaluation result can be output as follows:
```bash
$ python scripts/generate_results.py \
     --system-predict-txt $OUTPUT_DIR/predict_results_valid.txt \
     --input-file ../datasets/jcommonsenseqa-v1.1/valid-v1.1.json \
     --task-type swag \
     --additional-column-name-string q_id > $OUTPUT_DIR/predict_eval_results.tsv
```

## Links
- [JGLUE-evaluation-scripts](https://github.com/nobu-g/JGLUE-evaluation-scripts): this script can be used for all the fine-tuning experiments
