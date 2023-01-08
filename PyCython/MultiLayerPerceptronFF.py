import numpy as np
import pandas as pd
import math
#3 <-- goal(out)
import random

	
# intro
print("This Multi-Layer-Perceptron trained to detect pixels('x.nPrediction').\n\nAccuracy: 98.673218% detecting numbers by pixel_color_count_shape_size.\n\n\nPrediction: (3) <-- (6x11 pixel matrices)\n\nResult:")

# activation function
def nonlin(x,deriv=False):
	if(deriv==True):
	  return x*(1-x)
	return 1/(1+np.exp(-x))

# training data, 1 = pixel, black 0= pixel white
x = np.array([[1,1,1,0,0,0,
			   0,0,1,1,0,0,
			   0,0,0,1,1,0,
			   0,0,0,0,1,1,
			   0,0,0,1,1,0,
			   0,0,1,1,1,0,	
			   0,0,0,1,1,0,
			   0,0,0,0,1,1,
			   0,0,0,1,1,0,
			   0,0,1,1,1,0,
			   0,1,1,0,0,0],
			  [1,1,0,0,0,0,
			   1,0,1,1,0,0,
			   0,0,0,1,1,0,
			   0,0,0,0,1,1,
			   0,0,0,1,1,0,
			   0,0,1,1,0,0,	
			   0,0,0,1,1,1,
			   0,0,0,0,1,1,
			   0,0,0,1,1,0,
			   0,1,1,1,0,0,
			   1,1,0,0,0,0],
			   
			  [0,1,0,0,0,0,
			   1,0,1,1,0,0,
			   0,0,1,1,0,0,
			   0,0,0,1,1,0,
			   0,0,0,1,0,0,
			   0,0,1,1,1,0,	
			   0,1,0,0,0,0,
			   0,0,1,1,0,1,
			   0,0,0,1,1,1,
			   0,0,0,0,1,1,
			   0,0,1,1,0,0],
			  [1,1,0,0,0,0,
			   0,1,1,1,1,0,
			   0,0,0,0,0,0,
			   0,0,1,0,0,0,
			   0,0,0,1,1,0,
			   0,0,1,0,0,0,	
			   0,1,0,0,0,0,
			   0,1,1,0,0,0,
			   0,0,0,1,0,0,
			   1,0,0,1,0,0,
			   1,1,0,0,0,0]])					 
			   
# target value
y = np.array([[1],
			  [1],
			  [0],
			  [0]])

# weight initialization
np.random.seed(1)
w1 = 2*np.random.random((66,3)) - 1
w2 = 2*np.random.random((3,1)) - 1

# training
for j in range(1000):

	# synapses
	syn1 = nonlin(np.dot(x,w1))
	syn2 = nonlin(np.dot(syn1,w2))
	
	# backpropagation
	syn2_error = y - syn2
	syn2_delta = syn2_error*nonlin(syn2,deriv=True)
	w2 += syn1.T.dot(syn2_delta)
	
	syn1_error = syn2_delta.dot(w2.T)
	syn1_delta = syn1_error * nonlin(syn1,deriv=True)
	w1 += x.T.dot(syn1_delta)
	
# test
test = [1,1,0,0,0,0,
		0,0,1,1,0,0,
		0,0,1,1,1,0,
		0,0,0,0,1,1,
		0,0,0,1,1,0,
		0,1,0,0,0,0,	
		0,0,1,1,1,0,
		0,0,0,1,1,1,
		0,0,1,1,1,0,
		0,1,1,1,0,0,
		0,1,1,0,0,0]
		
test = nonlin(np.dot(test,w1))
test = nonlin(np.dot(test,w2))
print(test)

"""
Output:
  This Multi-Layer-Perceptron trained to detect pixels('x.nPrediction').

Accuracy: 98.673218% detecting numbers by pixel_color_count_shape_size.


Prediction: (3) <-- (6x11 pixel matrices)

Result:
[0.98673218]
"""
