# PyMath Lib ... In Progress
import sympy as sp
import math
import statistics
import numpy as np 
# 1/N E^N_i=1(y_i - ^y_i)**2
# Notations - Mathematical conversion

# simle indexing
x = [5, 25, 50]
i = 0
print(x[i])

print("Simple Indexing")
print("\n")

# extended for 2d-vectors(x_i_j)
x = [ [5, 25, 50], [75, 100, 105] ]
i = 0
j = 1
print(x[i][j])

print("Extension for 2d-vectors(X_i,j)")
print("\n")

# sigma
# E^N, i -> 1 * X_i
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = 0
N = len(x)
for i in range(N):
    res = res + x[i]
print(res)

print("Sigma")
print("\n")
# shorten above sigma with 'built-in fns'
# Sigma divisible by n elements of x = average
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = sum(x)
print(res)
print("Sigma-Shortened")
print("\n")

# Simple Average
# Sigma notation divisible by n of e to get avg. 
# 1 / N(E^E, i -> 1) * x_i
# re-use the similar code
print("Average")
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = 0
N = len(x)
for i in range(N):
    res = res + x[i]
average = res / N
print(average)
print("\n")

# Shortened code
print("Short-Avg")
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = sum(x) / len(x)
print(res)
print("\n")

# PI
# formula: BIG-PI(∏^N,_i->1) * x_i
# Finds the prod of all e in a v for a given range,\
# loop over vector 0[idx] N-1 * *
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
res = 1
N = len(x)
for i in range(N):
    res = res * x[i]
print(res)
print("BIG PI")
print("\n")

# ABS ||x||, ||y||
# Denotes abs of a int/num without a sign
x = 100
y = -20
abs(x) #100
abs(y) #200
print(abs(x))
print(abs(y))
print("Absolute value")
print("||x||")
print("||y||")
print("\n")
print("Norm of vect")
# norm -> calc magnitude of a v. ** e.elm[].sum.np.sqrt(sum)
x = [5, 25, 50]
print(math.sqrt(x[0]**2 + x[1]**2 + x[2]**2))
print("\n")
print("Belongs To ... 5 ∈ X")
# Checks if elm is partial of a set ~
X = {5, 25, 50}
print(5 in X)
print(set(X))
print("\n")

# Function
print("Function")
print("f : X → Y")
# denotes f(x) which inherits a domain X and mapts to range Y
# Pool of values X, operation to calc pool of values y
def f(X):
    Y = ...
    return Y
print(Y)
print("f : R → R")
