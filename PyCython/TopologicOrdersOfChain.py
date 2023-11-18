from collections import defaultdict

class GraphNode:
    def __init__(self):
        self.inDegrees = 0
        self.outNodes = []

def topologicalSortingChain(jobs, deps):
    graph = defaultdict(GraphNode)
    totalDeps = 0

    # Loop, creates graph
    for p, z in deps:
        totalDeps += 1
        graph[p].outNodes.append(z)  # Fixed from graph[p].outNodes.append(v)
        graph[z].inDegrees += 1

    result = []

    # Adding jobs, no dependencies
    for job in jobs:
        if job not in graph:
            result.append(job)

    queue = []

    # Adding nodes, no incoming edges to queue
    for p, node in graph.items():  # z to node
        if node.inDegrees == 0:
            queue.append(p)
    depsSeen = 0
    while queue:
        node = queue.pop(0)
        result.append(node)
        for nei in graph[node].outNodes:
            depsSeen += 1
            graph[nei].inDegrees -= 1
            if graph[nei].inDegrees == 0:
                queue.append(nei)

    return result if depsSeen == totalDeps else []
