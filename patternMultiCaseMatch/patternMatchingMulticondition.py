"""P ONEIL: Mutli-Case Handling Pattern Matching"""
import cmath
import itertools

def patternMatcher(pattern, string):
	if len(pattern) == 0 or len(pattern) > len(string):
		return []
	counts = getLetterCounts(pattern)
	if not counts:
		return []
	countsOfA, countsOfB, firstLetterA = counts
	if countsOfB == 0:
		lenA = len(string) // countsOfA
		if len(string) % countsOfA == 0:
			return [string[:lenA], ""] if firstLetterA == "x" else ["", string[:lenA]]
		return []
	if countsOfA == 0:
		lenB = len(string) // countsOfB
		if len(string) % countsOfB == 0:
			return [string[:lenB], ""] if firstLetterA == "x" else ["", string[:lenB]]
		return []
	possibleLenA_values = getPossibleLengths(countsOfA, countsOfB, len(string))
	for lenA in possibleLenA_values:
		lenB, remainder = divmod(len(string) - lenA * countsOfA, countsOfB)
		if remainder == 0:
			idxB = countsOfA * lenA
			stringA = string[:lenA]
			stringB = string[idxB: idxB + lenB]
			potentialMatch = "".join(stringA if char == firstLetterA else stringB for char in pattern)
			if potentialMatch == string:
				if firstLetterA == "x":
					return [stringA, stringB]
				return [stringB, stringA]
	return []
def getLetterCounts(pattern):
	countsOfA = 0
	countsOfB = 0
	firstLetterA = pattern[0]
	for char in pattern:
		if char == firstLetterA:
			countsOfA += 1
		else:
			countsOfB += 1
	return[countsOfA, countsOfB, firstLetterA]

def getPossibleLengths(countsOfA, countsOfB, totalLength):
	possible_lengths = []
	for lenA in range(1, (totalLength // countsOfA) + 1):
		lenB, remainder = divmod(totaalLength - (lenA * countsOfA), countsOfB)
		if remainder == 0:
			possible_lengths.append(lenA)
	return possible_lengths
