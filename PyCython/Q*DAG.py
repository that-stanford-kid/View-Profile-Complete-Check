import numpy as np
import matplotlib.pyplot as plt
import random
import math
from collections import namedtuple
import pandas as pd 


graph ='''
(0)     (3)-------(6)      (10)
 |                 |        |
 |                 |        |
 |                 |        |
(1)-----(4)-------(7)------(9)
         |         |
         |         |
         |         |
(2)-----(5)       (8)
'''
# Given respectively, Utilize the graph and return a trained agent using Reinforcement Learning(Q-Learning); regarding the optimal path from any node in range(9)


class Brain(object):
    def __init__(self):
        # REWARDING ARRAY
        # LINKS >= 9[REWARD==[100], else 0 if not 100 or else 0; if not either, else -1 if EXISTS ~ is -1]
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
        # Q, R |= brain function taught from the initialization of T -> 0
        self.Q = np.zeros((10, 10))
        self.target = 9
        self.gamma = 0.9
        self.episodes = 700

    def train(self):
        for i in range(self.episodes):
            s = np.random.randint(self.Q.shape[0])
            while s != self.target:
                av_a = np.where(self.R[s] >= 0)[0] # Available action(s) -> state s
                a = np.random.choice(av_a) # Cherrypick action in random state; offset biased choice

                max_a = np.max(np.where(self.R[a] >= 0)[0]) # MAX REWARD -> NEXT state action
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
    print("============PATH_METRICS=============")
    print('|Path from {} to 9 is {}|'.format(0, b.get_path(0)))
    print('|Path from {} to 9 is {}   |'.format(1, b.get_path(1)))
    print('|Path from {} to 9 is {}|'.format(2, b.get_path(2)))
    print('|Path from {} to 9 is {}   |'.format(3, b.get_path(3)))
    print('|Path from {} to 9 is {}      |'.format(4, b.get_path(4)))
    print('|Path from {} to 9 is {}   |'.format(5, b.get_path(5)))
    print('|Path from {} to 9 is {}|'.format(6, b.get_path(6)))
    print('|Path from {} to 9 is {}         |'.format(7, b.get_path(7)))
    print('|Path from {} to 9 is {}      |'.format(8, b.get_path(8)))
    print("=====================================\n\n")
    print(graph)

print("=====================================================================================")

import pylab as pl 
#import networkx as nxgraph

edges = [(0, 1), (1, 5), (5, 6), (5, 4), (1, 2), 
         (1, 3), (9, 10), (2, 4), (0, 6), (6, 7),
         (8, 9), (7, 8), (1, 7), (3, 9)]

goal = 10
"""G = nx.Graph()
G.add_edges_from(edges)
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos)
pl.show()"""


MATRIX_SIZE = 11
M = np.matrix(np.ones(shape =(MATRIX_SIZE, MATRIX_SIZE)))
M *= -1
  
for point in edges:
    print(point)
    if point[1] == goal:
        M[point] = 100
    else:
        M[point] = 0
  
    if point[0] == goal:
        M[point[::-1]] = 100
    else:
        M[point[::-1]]= 0
        # reverse of point
  
M[goal, goal]= 100
print("====================================================================================")
print(M)

print("====================================================================================")

Q = np.matrix(np.zeros([MATRIX_SIZE, MATRIX_SIZE]))
  
gamma = 0.75
# learning parameter
initial_state = 1
  
# Determines the available actions for a given state
def available_actions(state):
    current_state_row = M[state, ]
    available_action = np.where(current_state_row >= 0)[1]
    return available_action
  
available_action = available_actions(initial_state)
  
# Chooses one of the available actions at random
def sample_next_action(available_actions_range):
    next_action = int(np.random.choice(available_action, 1))
    return next_action
  
  
action = sample_next_action(available_action)

def update(current_state, action, gamma):
  
  max_index = np.where(Q[action, ] == np.max(Q[action, ]))[1]
  if max_index.shape[0] > 1:
      max_index = int(np.random.choice(max_index, size = 1))
  else:
      max_index = int(max_index)
  max_value = Q[action, max_index]
  Q[current_state, action] = M[current_state, action] + gamma * max_value
  if (np.max(Q) > 0):
    return(np.sum(Q / np.max(Q)*100))
  else:
    return (0)
# Updates the Q-Matrix according to the path chosen
  
update(initial_state, action, gamma)


scores = []
for i in range(1000):
    current_state = np.random.randint(0, int(Q.shape[0]))
    available_action = available_actions(current_state)
    action = sample_next_action(available_action)
    score = update(current_state, action, gamma)
    scores.append(score)
  
print("Trained Q matrix:")
print(Q / np.max(Q)*100)

  
# Testing
current_state = 0
steps = [current_state]
  
while current_state != 10:
  
    next_step_index = np.where(Q[current_state, ] == np.max(Q[current_state, ]))[1]
    if next_step_index.shape[0] > 1:
        next_step_index = int(np.random.choice(next_step_index, size = 1))
    else:
        next_step_index = int(next_step_index)
    steps.append(next_step_index)
    current_state = next_step_index
print("==================================================================================")
print("Most efficient path:")

print(steps)
