def minCount(comps):
    if not comps:
        return 0
    counts = [1] * len(comps)
    # Left to right
    for i in range(1, len(comps)):
        if comps[i] > comps[i - 1]:
            counts[i] = counts[i - 1] + 1
    # Right to left
    for i in range(len(comps) - 2, -1, -1):
        if comps[i] > comps[i + 1]:
            counts[i] = max(counts[i], counts[i + 1] + 1)

    return sum(counts)
