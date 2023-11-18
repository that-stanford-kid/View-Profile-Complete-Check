def smallestDifference(arrOne, arrTwo):
    arrOne.sort()
    arrTwo.sort()
    idxOne = idxTwo = 0
    smallest = float('inf')
    current = float('inf')
    smallestPairDiff = []
    while idxOne < len(arrOne) and idxTwo < len(arrTwo):
        firstNum = arrOne[idxOne]
        secondNum = arrTwo[idxTwo]

        if firstNum < secondNum:
            current = secondNum - firstNum
            idxOne += 1
        elif secondNum < firstNum:
            current = firstNum - secondNum
            idxTwo += 1
        else:
            return [firstNum, secondNum]

        if smallest > current:
            smallest = current
            smallestPair = [firstNum, secondNum]

    return smallestPairDiff
