import math
import argparse
import codecs
from collections import defaultdict
import random

"""
This file is part of the computer assignments for the course DD1418 at KTH.
"""

class Generator(object) :
    """
    This class generates words from a language model.
    """
    def __init__(self):
    
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
        # Important that it is named self.logProb for the --check flag to work
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


    def read_model(self,filename):
        """
        Reads the contents of the language model file into the appropriate data structures.

        :param filename: The name of the language model file.
        :return: True if the entire file could be processed, False otherwise.
        """

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.unique_words, self.total_words = map(int, f.readline().strip().split(' '))
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

    def generate(self, w, n):
        """
        Generates and prints n words, starting with the word w, and following the distribution
        of the language model.
        """ 
        # YOUR CODE HERE
        if w not in self.index:
            print("The word '{}' is not in the model".format(w))
            return

        i = self.index[w]
        words = [w]

        for _ in range(n - 1):
            successors = self.bigram_prob[i]

            if successors:
                # As in Fig. 3.3 of the book: lay the probabilities of the
                # possible next words out on the number line [0, 1], pick a
                # random point, and choose the word whose interval contains it.
                r = random.random()
                cumulative = 0.0
                next_i = None
                for j, log_prob in successors.items():
                    cumulative += math.exp(log_prob)
                    if r < cumulative:
                        next_i = j
                        break
                if next_i is None:
                    # Rounding errors may make the sum slightly less than 1.
                    next_i = j
            else:
                # No known successor: pick any word with uniform probability.
                next_i = random.randrange(self.unique_words)

            i = next_i
            words.append(self.word[i])

        print(' '.join(words))


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='BigramTester')
    parser.add_argument('--file', '-f', type=str,  required=True, help='file with language model')
    parser.add_argument('--start', '-s', type=str, required=True, help='starting word')
    parser.add_argument('--number_of_words', '-n', type=int, default=100)

    arguments = parser.parse_args()

    generator = Generator()
    generator.read_model(arguments.file.strip())
    generator.generate(arguments.start.strip(),arguments.number_of_words)

if __name__ == "__main__":
    main()
