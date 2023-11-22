def wArea(heights):
    if not heights:
        return 0
    leftMax, rightMax = [0] * len(heights), [0] * len(heights)
    leftMax[0], rightMax[-1] = heights[0], heights[-1]
    # leftMax and rightMax arrs
    for i in range(1, len(heights)):
        leftMax[i] = max(leftMax[i - 1], heights[i])
        rightMax[-i - 1] = max(rightMax[-i], heights[-i - 1])
    # Calc * watera
    w = 0
    for i in range(len(heights)):
        w += min(leftMax[i], rightMax[i]) - heights[i]

    return w
