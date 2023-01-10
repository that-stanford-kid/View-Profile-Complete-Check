import numpy as np

def laplace_expansion(matrix, i):
    n = matrix.shape[0]
    submatrix = matrix[1:, [j for j in range(n) if j != i]]
    subdet = np.linalg.det(submatrix)
    return ((-1 ** i) * matrix[0][i] * subdet
  
 def determinant(matrix):
     # calc determinant of ** matrix from Laplace
   return sum(laplace_expansion(matrix, i) for i in range(matrix.shape[0]))
   
 A = np.array([[11, 3.14159, 3**3], [4, -2, 6], [7, -8, -9]])
 det_A = determinant(A)
 print("Determinant of A: ", det_A)
