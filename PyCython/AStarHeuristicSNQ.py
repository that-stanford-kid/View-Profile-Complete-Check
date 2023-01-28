from heapq import heappush, heappop
    
class PriorityQueue: 
    def __init__(self, iterable=[]): 
        self.heap = [] 
        for value in iterable: 
            heappush(self.heap, (0, value)) 
    def add(self, value, priority=0):
        heappush(self.heap, (priority, value)) 
    def pop(self):
        priority, value = heappop(self.heap) 
        return value 
    def notEmpty(self):
        return bool(self.heap)
def aStarSearch(start, goal_function, successor_function, heuristic ): 
    visited = set() 
    came_from = dict() 
    distance = {start: 0} 
    partition = PriorityQueue() 
    partition.add(start) 
    while partition.notEmpty():
        node = partition.pop()
        if node in visited:
            continue 
        if goal_function(node):
            end = node
            reverse_path = [end] 
            while end != start: 
                end = came_from[end] 
                reverse_path.append(end) 
            return list(reversed(reverse_path))
        visited.add(node) 
        for successor in successor_function(node): 
            partition.add( successor, priority = distance[node] + 1 + heuristic(successor) ) 
            if (successor not in distance or distance[node] + 1 < distance[successor]):
                distance[successor] = distance[node] + 1
                came_from[successor] = node
    return None
def getGoal(grid):
    M = len(grid)
    N = len(grid[0]) 
    def didReachCorner(cell): 
        return cell == (M-1, N-1) 
    return didReachCorner
def getSuccessor(grid):
    def getClearAdjacentCells(cell): 
        i, j = cell 
        return ( 
            (i + a, j + b) 
            for a in (-1, 0, 1) 
            for b in (-1, 0, 1) 
            if a != 0 or b != 0 
            if 0 <= i + a < len(grid) 
            if 0 <= j + b < len(grid[0]) 
            if grid[i + a][j + b] == 0 
        )
    return getClearAdjacentCells
def getHeuristic(grid):
    M, N = len(grid), len(grid[0]) 
    (a, b) = goal_cell = (M - 1, N - 1) 
    def getClearPathDistance(cell): 
        (i, j) = cell 
        return max(abs(a - i), abs(b - j)) 
    return getClearPathDistance
def shortestPathMap(grid):
    shortest_path = aStarSearch(
        (0, 0),
        getGoal(grid),
        getSuccessor(grid),
        getHeuristic(grid) 
    )
    if shortest_path is None or grid[0][0] == 1:
        print('No solution')
    else:
        print("START => ", end="")
        for (x, y) in shortest_path:
            print((x,y), end=" => ")
            grid[x][y] = '\u26ab'
        print("GOAL\n")
        for row in grid:
            for cell in row:
                print(f"{cell}  ", end = " ")
            print("\n")
maze = [
        [0,0,0,1,0,0,1,0], 
        [0,0,0,1,0,0,0,0],
        [1,1,1,0,0,1,1,1],
        [0,1,1,1,0,0,0,0], 
        [0,0,0,0,0,1,1,0], 
        [1,0,1,0,0,1,0,0], 
        [1,1,0,0,1,0,0,0], 
        [0,0,0,0,0,0,0,0]
    ]

shortestPathMap(maze)
"""
START => (0, 0) => (1, 1) => (1, 2) => (2, 3) => (3, 4) => (4, 4) => (5, 4) => (6, 5) => (6, 6) => (7, 7) => GOAL

⚫   0   0   1   0   0   1   0   

0   ⚫   ⚫   1   0   0   0   0   

1   1   1   ⚫   0   1   1   1   

0   1   1   1   ⚫   0   0   0   

0   0   0   0   ⚫   1   1   0   

1   0   1   0   ⚫   1   0   0   

1   1   0   0   1   ⚫   ⚫   0   

0   0   0   0   0   0   0   ⚫   
"""
