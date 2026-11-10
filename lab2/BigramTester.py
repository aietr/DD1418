#  -*- coding: utf-8 -*-
import math
import argparse
import re
import codecs
from collections import defaultdict

"""
This file is part of the computer assignments for the course DD1418 at KTH.
"""

class BigramTester(object):
    def __init__(self):
        """
        This class reads a language model file and a test file, and computes
        the entropy of the latter. 
        """
        # The mapping from words to identifiers.
        self.index = {}

        # The mapping from identifiers to words.
        self.word = {}

        # An array holding the unigram counts.
        self.unigram_count = {}

        # The bigram log-probabilities.
        self.bigram_prob = defaultdict(dict)

        # Number of unique words (word forms) in the training corpus.
        self.unique_words = 0

        # The total number of words in the training corpus.
        self.total_words = 0

        # The average log-probability (= the estimation of the entropy) of the test corpus.
        self.logProb = 0

        # The identifier of the previous word processed in the test corpus. Is -1 if the last word was unknown.
        self.last_index = -1

        # The fraction of the probability mass given to unknown words.
        self.lambda3 = 0.000001

        # The fraction of the probability mass given to unigram probabilities.
        self.lambda2 = 0.01 - self.lambda3

        # The fraction of the probability mass given to bigram probabilities.
        self.lambda1 = 0.99

        # The number of words processed in the test corpus.
        self.test_words_processed = 0


    def read_model(self, filename):
        """
        Reads the contents of the language model file into the appropriate data structures.

        :param filename: The name of the language model file.
        :return: <code>true</code> if the entire file could be processed, false otherwise.
        """

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.unique_words, self.total_words = map(int, f.readline().strip().split(' '))
                # identifier, word, unigram count.
                for _ in range(self.unique_words):
                    i, word, count = f.readline().strip().split(' ')
                    i, count = int(i), int(count)
                    self.index[word] = i
                    self.word[i] = word
                    self.unigram_count[i] = count

                # Read the bigram lines until the end marker -1.
                for line in f:
                    line = line.strip()
                    if line == '-1':
                        break
                    i, j, log_prob = line.split(' ')
                    self.bigram_prob[int(i)][int(j)] = float(log_prob)
                return True
        except IOError:
            print("Couldn't find bigram probabilities file {}".format(filename))
            return False


    def compute_entropy_cumulatively(self, word):
        """
        Adds the contribution of one test word to the running entropy estimate
            H = -1/N * sum_i log P(w_{i-1} w_i)
        where P is the linearly interpolated probability
            P = lambda1 * P(w_i | w_{i-1}) + lambda2 * P(w_i) + lambda3

        :param word: The current word in the test corpus.
        """
        
        prob = self.lambda3

        if word in self.index:
            i = self.index[word]

            # Unigram part: P(w_i) = C(w_i) / N
            prob += self.lambda2 * self.unigram_count[i] / self.total_words

            # Bigram part: P(w_i | w_{i-1}), only if the previous word was known
            # and the bigram was seen in training.
            if self.last_index != -1 and i in self.bigram_prob[self.last_index]:
                prob += self.lambda1 * math.exp(self.bigram_prob[self.last_index][i])

            self.last_index = i
        else:
            # Unknown word: no bigram can start from it.
            self.last_index = -1

        # Update the running average of -log P incrementally.
        self.test_words_processed += 1
        self.logProb += (-math.log(prob) - self.logProb) / self.test_words_processed

    def process_test_file(self, test_filename):
        """
        Reads and processes the test file one word at a time. 

        :param test_filename: The name of the test corpus file.
        :return: True if the entire file could be processed, False otherwise.
        """
        try:
            with open(test_filename, 'r', encoding='utf-8') as f:
                text = f.read().encode('utf-8').decode().lower()
                self.tokens = re.findall(r"[\w'-]+|[\".,!?;]", text)
                for token in self.tokens:
                    self.compute_entropy_cumulatively(token)
            return True
        except IOError:
            print('Error reading testfile')
            return False


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='BigramTester')
    parser.add_argument('--file', '-f', type=str,  required=True, help='file with language model')
    parser.add_argument('--test_corpus', '-t', type=str, required=True, help='test corpus')

    arguments = parser.parse_args()

    bigram_tester = BigramTester()
    bigram_tester.read_model(arguments.file.strip())
    bigram_tester.process_test_file(arguments.test_corpus.strip())
    print('Read {0:d} words. Estimated entropy: {1:.2f}'.format(bigram_tester.test_words_processed, bigram_tester.logProb))

if __name__ == "__main__":
    main()
