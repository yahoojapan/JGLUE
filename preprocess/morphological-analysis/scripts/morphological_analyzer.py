import os
import sys

import zenhan


class Word(object):
    def __init__(self, string, pos=None, offset=0):
        self.string = string
        self.pos = pos
        self.start_position = offset
        self.end_position = offset + len(self.string) - 1


class MorphologicalAnalyzer(object):
    def __init__(self, analyzer,
                 mecab_dic_dir=None,
                 h2z=False):
        self._analyzer = analyzer
        self._h2z = h2z

        if self._analyzer == "jumanpp" or self._analyzer == "juman":
            from pyknp import Juman
            self._juman = Juman(jumanpp=True if self._analyzer == "jumanpp" else False)
        elif self._analyzer == "mecab":
            import MeCab
            tagger_option_string = ""
            if mecab_dic_dir is not None:
                tagger_option_string += f" -d {mecab_dic_dir}"
            self._mecab = MeCab.Tagger(tagger_option_string)

    def get_words(self, string):
        words = []
        offset = 0

        if self._analyzer == "jumanpp" or self._analyzer == "juman":
            try:
                result = self._juman.analysis(string)
            except ValueError as e:
                print(f"{e}. skip sentence: {string}", file=sys.stderr)
                return []

            for mrph in result.mrph_list():
                words.append(Word(mrph.midasi, pos=mrph.hinsi, offset=offset))
                offset += len(mrph.midasi)
        elif self._analyzer == "mecab":
            self._mecab.parse("")
            node = self._mecab.parseToNode(string)
            while node:
                word = node.surface
                pos = node.feature.split(",")[0]
                if node.feature.split(",")[0] != "BOS/EOS":
                    words.append(Word(word, pos=pos, offset=offset))
                    offset += len(word)
                node = node.next
        elif self._analyzer == "char":
            for char in list(string):
                words.append(Word(char, offset=offset))
                offset += 1
        else:
            NotImplementedError(f"unknown analyzer: {self._analyzer}")

        return words

    def get_tokenized_string(self, string):
        if self._h2z is True:
            string = zenhan.h2z(string)

        words = self.get_words(string)
        if len(words) > 0:
            return " ".join([word.string for word in words])
        else:
            return None
