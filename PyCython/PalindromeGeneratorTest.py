"""
Created on Fri Jan 13 10:31:53 2023

@author: p0ne
"""
import string
import random

def generate_test_words(num_words, word_length):
    test_words = []
    for _ in range(num_words):
        word = ''.join(random.choice(string.ascii_letters) for _ in range(word_length))
        test_words.append(word)
    return test_words

def palindromePartitionMinCuts(string):
    n = len(string)
    # Initialize a 2D array to store whether substrings are palindromes or not
    palindromes = [[False for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            if string[i] == string[j] and (i - j <= 2 or palindromes[j+1][i-1]):
                palindromes[j][i] = True
    # Initialize an array to store the minimum number of cuts for each substring
    cuts = [float('inf')] * n
    for i in range(n):
        if palindromes[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = min(cuts[j] + 1 for j in range(i) if palindromes[j+1][i])
    return cuts[-1]

test_words = generate_test_words(10, 5)
for word in test_words:
    print(f'Minimum cuts required for "{word}" to be partitioned into palindromes: {palindromePartitionMinCuts(word)}')
