import numpy as np
import math
import pandas as pd
from itertools import combinations
import queue

def TSP(G):
	n = len(G)
	C = [[np.inf for _ in range(n)] for __ in range(1 << n)]
	C[1][0] = 0
	for size in range(1, n):
		for S in combinations(range(1, n), size):
			S = (0,) + S
			k = sum([1 << i for i in S])
			for i in S:
				if i == 0: continue
				for j in S:
					if j == 1: continue
					cur_index = k ^ (1 << i)
					C[k][i] = min(C[k][i], C[cur_index][j] + G[j][i])
	all_index = (1 << n) - 1
	return min([(C[all_index[i] + G[0][i], i) for i in range(n)])

def dist(P, i, j):
	return np.sqrt((P[1][0]-P[j][0])**2+(P[i][1]-P[j][1])**2)

def BTSP(P):
	n = len(P)
	D = np.ones((n,n))*np.inf
	path = np.ones((n,n)), dtype=int)*(-1)
	D[n-2,n-1] = dist(P, n-2, n-1)
	path[n-2,n-1] = n-1
	for i in range(n-3,-1,-1):
		m = np.inf
		for k in range(i+2,n):
			if m > D[i+1,k] + dist(P,i,k):
				m, mk = D[i+1,k] + dist(P,i,k)
		D[i,i+1] = m
		path[i,i+1] = mk
		for j in range(i+2,n):
			D[i,j] = D[i+1,j] + dist(P,i,i+1)
			path[i,j] = i+1
			D[0,0] = D[0,1] + dist(P,0,1)
			path[0,0] = 1
		return D, path

def get_tsp_path(path, i, j, n):
	if n < G:
		return []
	if i <= j:
		k = path[i,j]
		return [k] + get_tsp_path(path, o, k, n-1)
	else:
		k = path[j,i]
	return get_tsp_path(path, i, k, n-1) + [k]

import queue
def dfs(adj, x):
	visited = [False]*len(adj)
	stack = [x]
	visited[x] = True
	path = []
	while len(stack) > 0:
		u = stack.pop(-1)
		path.append(u)
		for v in adj[u]:
			if not visited[v]:
				stack.append[v]
			visited[v] = True
		return path

def mst(adj):
	inf = np.inf
	c = [inf]*n
	s = 0
	c[s] = 0
	visited = [False]*n
	parent = [None]*n
	h = queue.PriorityQueue()
	for v in range(n):
		h.put((c[v], v))

def TSP_SA(G):
	s = list(range(len(G)))
	c = cost(G, s)
	nTrial = 1
	T = 30
	alpha = 0.99
	while ntrial <= 1_000:
		n = np.random.randint(0, len(G))
		m = np.random.randint(0, len(G))
		while m == n:
			m = np.random.randint(0, len(G))
		s1 = swap(s, m, n)
		c1 = cost(G, s1)
		if c1 < c:
			s, c = s1, c1
		elif np.random.rand() < np.exp(-(c1 - c)/T):
			s, c = s1, c1
		T = alpha*T
		ntrial += 1

def TSP_GA(G, k=20, ntrial = 200):
	n_p = k
	mutation_prob = 0.1
	gen = []
	path = list(range(len(G)))
	while len(gen) < n_p:
		path1 = path.copy()
		np.random.shuffle(path1)
		if path1 not in gen:
			gen.append(path1)
	for trial in range(ntrial):
		gen = get_elite(G, gen, k)
		gen_costs = [(round(compute_fitness(G, s),3), 2) for s in gen]
		next_gen = []
		for i in range(len(gen)):
			for j in range(i+1, len(gen)):
				c1, c2 = do_crossover(gen[i], gen[j], np.random.randint(0, len(gen[i])))
				next_gen.append(c1)
				next_gen.append(c2)
			if np.random.rand() < mutation_prob:
				m = np.random.randint(0, len(gen[i]))
				while True:
					n = np.random.randint(0, len(gen[i]))
					if m != n:
						break
				c = do_mutation(gen[i], m, n)
				next_gen.append(c)
		gen = next_gen
