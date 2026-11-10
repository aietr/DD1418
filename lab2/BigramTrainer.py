#  -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math
import argparse
import re
import os
from collections import defaultdict
import codecs

"""
This file is part of the computer assignments for the course DD1418 at KTH. 
"""


class BigramTrainer(object):
    """
    This class constructs a bigram language model from a corpus.
    """

    def process_files(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read().encode('utf-8').decode().lower()
        self.tokens = re.findall(r"[\w'-]+|[\".,!?;]", text)
        for token in self.tokens:
            self.process_token(token)


    def process_token(self, token):
        """
        Processes one word in the training corpus, and adjusts the unigram and
        bigram counts.

        :param token: The current word to be processed.
        """
        # Give every new word form the next free identifier.
        if token not in self.index:
            self.index[token] = self.unique_words
            self.word[self.unique_words] = token
            self.unique_words += 1
        i = self.index[token]

        # Unigram count C(w_n).
        self.unigram_count[i] += 1
        self.total_words += 1

        # Bigram count C(w_{n-1} w_n), if there is a previous word.
        if self.last_index != -1:
            self.bigram_count[self.last_index][i] += 1

        self.last_index = i


    def stats(self):
        """
        Creates a list of rows to print of the language model.
        """
        rows_to_print = []

        # First row: V and N.
        rows_to_print.append('{} {}'.format(self.unique_words, self.total_words))

        # One row per word: identifier, word, unigram count.
        for i in range(self.unique_words):
            rows_to_print.append('{} {} {}'.format(i, self.word[i], self.unigram_count[i]))

        # One row per non-zero bigram, using the relative frequency (MLE)
        #   P(w_n | w_{n-1}) = C(w_{n-1} w_n) / C(w_{n-1})
        # and storing its natural logarithm, log C(w_{n-1} w_n) - log C(w_{n-1}),
        # with 15 decimals.
        for i in range(self.unique_words):
            for j, count in self.bigram_count[i].items():
                log_prob = math.log(count) - math.log(self.unigram_count[i])
                rows_to_print.append('{} {} {:.15f}'.format(i, j, log_prob))

        # End of file marker.
        rows_to_print.append('-1')

        return rows_to_print


    def __init__(self):
        """
        Constructor. Processes the file f and builds a language model
        from it.

        :param f: The training file.
        """

        # The mapping from words to identifiers.
        self.index = {}

        # The mapping from identifiers to words.
        self.word = {}

        # An array holding the unigram counts.
        self.unigram_count = defaultdict(int)

        """
        The bigram counts. Since most of these are zero (why?), we store these
        in a hashmap rather than an array to save space (and since it is impossible
        to create such a big array anyway).
        """
        self.bigram_count = defaultdict(lambda: defaultdict(int))

        # The identifier of the previous word processed.
        self.last_index = -1

        # Number of unique words (word forms) in the training corpus.
        self.unique_words = 0

        # The total number of words in the training corpus.
        self.total_words = 0


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='BigramTrainer')
    parser.add_argument('--file', '-f', type=str,  required=True, help='file from which to build the language model')
    parser.add_argument('--destination', '-d', type=str, help='file in which to store the language model')

    arguments = parser.parse_args()

    bigram_trainer = BigramTrainer()

    bigram_trainer.process_files(arguments.file.strip())

    stats = bigram_trainer.stats()
    if arguments.destination:
        with open(arguments.destination.strip(), 'w', encoding='utf-8') as f:
            for row in stats:
                f.write(row + '\n')
    else:
        for row in stats:
            print(row)


if __name__ == "__main__":
    main()
