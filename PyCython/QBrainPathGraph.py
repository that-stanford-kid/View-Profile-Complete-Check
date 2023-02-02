# that-stanford-kid
import numpy as np
import matplotlib.pyplot as plt
import random
import math
from collections import namedtuple

graph ='''
(0)     (3)-------(6)      (10)
 |                 |        |
 |                 |        |
 |                 |        |
(1)-----(4)-------(7)------(9)
		 |		   |
		 |	 	   |
		 | 		   |
(2)-----(5)       (8)
'''
# Utilize the graph and return a trained agent using RL(Q-Learning) for node in range()

class Brain(object):
	def __init__(self):
		# REWARDING ARRAY
		# LINKS >= 0[REWARD==[100], else 0 if not 100 or else 0; if not either, else -1 if EXISTS ~ os -1]
		self.R = np.array([
			# 0   1   2   3   4   5   6   7   8   9
			[-1,  0, -1, -1, -1, -1, -1, -1, -1, -1], # 0
			[ 0, -1,  0, -1,  0, -1, -1, -1, -1, -1], # 1
			[-1,  0, -1, -1, -1, -1, -1, -1, -1, -1], # 2
			[-1, -1, -1, -1,  0, -1,  0, -1, -1, -1], # 3
			[-1,  0, -1,  0, -1,  0, -1,  0, -1, -1], # 4
			[-1, -1, -1, -1,  0, -1, -1, -1, -1, -1], # 5
			[-1, -1, -1,  0, -1, -1, -1, -1, -1, -1], # 6
			[-1, -1, -1, -1,  0, -1, -1, -1,  0,100], # 7 <- REWARD
			[-1, -1, -1, -1, -1, -1, -1,  0, -1, -1], # 8
			[-1, -1, -1, -1, -1, -1, -1,  0, -1,100], # 9 <- REWARD
		])
		# Q, R |= brain func from init(T -> 0)
		self.Q = np.zeros((10, 10))
		self.target = 9
		self.gamma = 0.9
		self.episodes = 700
		
	def train(self):
		for i in range(self.episodes):
			s = np.random.randint(self.Q.shape[0])
			while s != self.target:
				av_a = np.where(self.R[s] >= 0)[0] # Av_a (s) -> state s
				a = np.random.choice(av_a) # Cherrypick action to offset biased choice
				
				max_a = np.max(np.where(self.R[a] >= 0)[0]) # MAX REWARD -> NEXT s,a
				self.Q[s, a] = self.R[s, a] + self.gamma * max_a
				s = a
	def get_path(self, start):
		s = start
		states = [s]
		while s != self.target:
			s = np.where(self.Q[s] == np.max(self.Q[s]))[0][0]
			states.append(s)
		return states
	
if __name__ == '__main__':
	b = Brain()
	b.train()
	print("============PATH_METRICS============")
	print('|Path from {} to 9 is {}|'.format(0, b.get_path(0)))
	print('|Path from {} to 9 is {}   |'.format(1, b.get_path(1)))
	print('|Path from {} to 9 is {}|'.format(2, b.get_path(2)))
	print('|Path from {} to 9 is {}   |'.format(3, b.get_path(3)))
	print('|Path from {} to 9 is {}      |'.format(4, b.get_path(4)))
	print('|Path from {} to 9 is {}   |'.format(5, b.get_path(5)))
	print('|Path from {} to 9 is {}|'.format(6, b.get_path(6)))
	print('|Path from {} to 9 is {}         |'.format(7, b.get_path(7)))
	print('|Path from {} to 9 is {}      |'.format(8, b.get_path(8)))
	print("====================================\n\n")
	print(graph)


# Output
============PATH_METRICS=============
|Path from 0 to 9 is [0, 1, 4, 7, 9]|
|Path from 1 to 9 is [1, 4, 7, 9]   |
|Path from 2 to 9 is [2, 1, 4, 7, 9]|
|Path from 3 to 9 is [3, 4, 7, 9]   |
|Path from 4 to 9 is [4, 7, 9]      |
|Path from 5 to 9 is [5, 4, 7, 9]   |
|Path from 6 to 9 is [6, 3, 4, 7, 9]|
|Path from 7 to 9 is [7, 9]         |
|Path from 8 to 9 is [8, 7, 9]      |
=====================================

'''(0)     (3)-------(6)      (10)
    |                 |        |
    |                 |        |
    |                 |        |
   (1)-----(4)-------(7)------(9)
		    |		  |
		    |	 	  |
		    | 		  |
   (2)-----(5)       (8)
'''
