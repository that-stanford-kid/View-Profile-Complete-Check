"""ROC Calculation."""
def solution(X, Y):
    auroc = 0
    for i in range(1, len(X)):
        auroc += (X[i]-X[i-1])*(Y[i]+Y[i-1]) / 2
    return auroc

X = [0.00, 0.2, 0.33, 0.43, 0.63, 0.66, 1.00]
Y = [0.00, 0.25, 0.25, 0.50, 0.50, 1.00, 1.00]
print(solution(X, Y))
