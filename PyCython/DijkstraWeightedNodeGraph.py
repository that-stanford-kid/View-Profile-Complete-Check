import heapq
import networkx as nx

def djk_algo(graph, start, goal):
	shortest_dist = {}
	track_predecessor = {}
	unseen_nodes = []
	heapq.heappush(unseen_nodes, (0, start)) #p_node
	inf = float("inf")
	
	for node in graph:
		shortest_dist[node] = inf
	shortest_dist[start] = 0
	
	while unseen_nodes:
		current_dist, current_node = heapq.heappop(unseen_nodes)
		
		if current_dist > shortest_dist[current_node]:
			continue
		
		for neigh, weight in graph[current_node].items():
			dist = current_dist + weight
			
			if dist < shortest_dist[neigh]:
				shortest_dist[neigh] = dist
				track_predecessor[neigh] = current_node
				heapq.heappush(unseen_nodes, (dist, neigh))
	
	track_path = []
	current_node = goal
	
	while current_node != start:
		try:
			track_path.insert(0, current_node)
			current_node = track_predecessor[current_node]
			
		except KeyError:
			print("Path not in reach")
			break
	
	track_path.insert(0, start)
	# --oo |= inf
	if shortest_dist[goal] != inf:
		print("Shortest dist is " + str(shortest_dist[goal]))
		print("Optimal route of path is " + str(track_path))
		print("Queue FIFO - value of x1 for n queue " + str(track_path))
