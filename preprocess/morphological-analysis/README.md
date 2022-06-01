# Morphological Analysis

Run the following command:

(Please replace `/somewhere/jumandic` with your installed MeCab dictionary directory in the following command.)
```bash
$ cd preprocess/morphological-analysis/scripts
$ python apply_morphological_analysis_all.py \
         --datasets-json ../config/datasets.json \
         --data-dir ../../../datasets \
         --mecab-dic-dir /somewhere/jumandic \
         --h2z
```

It will take around five minutes. The processed data will be generated under the `../../datasets/*_{mecab,jumanpp}/` directory.
