# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import codecs
from collections import defaultdict

"""
This file is part of the computer assignments for the course DD1418 at KTH.

This program computes the minimum-cost alignment of two strings.
"""

"""
When printing the results, only print BREAKOFF characters per line.
"""
BREAKOFF = 60


def compute_backpointers(s0, s1):
    """
    Computes and returns the backpointer table (see Jurafsky and Martin, 
    Fig. 2.21) arising from the calculation of the minimal edit distance 
    of two strings s0 and s1.

    The backpointer table has two dimensions: the row and column indices 
    of the table in Fig 2.21. The value are the coordinates of the cell
    the backpointer is pointing to. For example, if the backpointer from 
    cell (5,5) is to cell (5,4), then backptr[5][5] = (5,4).

    :param s0: The first string.
    :param s1: The second string.
    :return: The backpointer array.
    """
    
    if s0 == None or s1 == None:
        raise Exception('Both s0 and s1 has to be set')

    backptr = defaultdict(lambda:defaultdict(int))

    # n <- LENGTH(source), m <- LENGTH(target)
    n, m = len(s0), len(s1)

    # Create a distance matrix D[n+1, m+1]
    D = [[0] * (m + 1) for _ in range(n + 1)]

    # Initialization
    # D[0,0] = 0  (already 0)
    for i in range(1, n + 1):
        D[i][0] = D[i-1][0] + 1          # del-cost = 1
        backptr[i][0] = (i - 1, 0)
    for j in range(1, m + 1):
        D[0][j] = D[0][j-1] + 1          # ins-cost = 1
        backptr[0][j] = (0, j - 1)

    # Recurrence relation
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            delete = D[i-1][j]   + 1
            sub    = D[i-1][j-1] + subst_cost(s0[i-1], s1[j-1])
            insert = D[i][j-1]   + 1

            D[i][j] = min(sub, delete, insert)

            if D[i][j] == sub:
                backptr[i][j] = (i - 1, j - 1)
            elif D[i][j] == delete:
                backptr[i][j] = (i - 1, j)
            else:
                backptr[i][j] = (i, j - 1)

    # D[n][m]
    return backptr


    return backptr




def subst_cost(c0, c1):
    """
    The cost of a substitution is 2 if the characters are different
    or 0 otherwise (when, in fact, there is no substitution).
    """
    return 0 if c0 == c1 else 2



def align(s0, s1, backptr):
    """
    Finds the best alignment of two different strings s0 and s1 given
    a table of backpointers.

    The alignment is made by padding the input strings with spaces. If, 
    for instance, the strings are 'around' and 'rounded', then the 
    padded strings should be 'around  ' and ' rounded'.

    :param s0: The first string.
    :param s1: The second string.
    :param backptr: The backpointer table as returned by the 
    'compute_backpointes' function above.
    :return: A pair of (r1,r2), where r1 is s1 padded with spaces, as
    exemplified above, and r2 is s2 padded with spaces. 
    """

    r0,r1 = '',''

    # Start in the bottom right cell
    i, j = len(s0), len(s1)

    # Keep following arrows until we reach the top left
    while (i, j) != (0, 0):
        pi, pj = backptr[i][j] 

        if pi == i - 1 and pj == j - 1:
            # Diagonal
            r0 += s0[i-1]
            r1 += s1[j-1]
        elif pi == i - 1:
            # Up
            r0 += s0[i-1]
            r1 += ' '
        else:
            # Left
            r0 += ' '
            r1 += s1[j-1]

        i, j = pi, pj               

    # flip the order
    return (r0[::-1], r1[::-1])




def print_alignment(s0,s1):
    """
    Prints two aligned strings (= strings padded with spaces).

    :param s0,s1: Two strings of equal length
    """
    assert len(s0) == len(s1)
    start_index = 0
    while start_index < len(s0):
        end_index = min(start_index+BREAKOFF, len(s0))
        print_list = ['', '', '']
        for i in range(start_index, end_index):
            print_list[0] += s0[i]
            print_list[1] += '|' if s0[i] == s1[i] else ' '
            print_list[2] += s1[i]

        for x in print_list:
            print(x)
        start_index += BREAKOFF


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Aligner')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str, nargs=2, help='align two strings')
    group.add_argument('--string', '-s', type=str, nargs=2, help='align the contents of two files')

    arguments = parser.parse_args()

    if arguments.file:
        f1, f2 = arguments.file
        with codecs.open(f1, 'r', 'utf-8') as f:
            s1 = f.read().replace('\r', '').replace('\n', ' ')
        with codecs.open(f2, 'r', 'utf-8') as f:
            s2 = f.read().replace('\r', '').replace('\n', ' ')

    elif arguments.string:
        s1, s2 = arguments.string
    
    padded1, padded2 = align(s1, s2, compute_backpointers(s1, s2))
    print_alignment( padded1, padded2 )

    
if __name__ == "__main__":
    main()
