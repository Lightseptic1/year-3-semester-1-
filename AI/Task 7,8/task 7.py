from collections import deque
import heapq
import time

maze = [
(0, 0, 1), (1, 0, 1), (2, 0, 0), (3, 0, 1), (4, 0, 1), (5, 0, 1), (6, 0, 0), (7, 0, 1), (8, 0, 1), (9, 0, 1),
(0, 1, 0), (1, 1, 1), (2, 1, 0), (3, 1, 1), (4, 1, 0), (5, 1, 1), (6, 1, 1), (7, 1, 0), (8, 1, 1), (9, 1, 0),
(0, 2, 1), (1, 2, 1), (2, 2, 1), (3, 2, 1), (4, 2, 0), (5, 2, 1), (6, 2, 0), (7, 2, 1), (8, 2, 1), (9, 2, 1),
(0, 3, 1), (1, 3, 0), (2, 3, 1), (3, 3, 0), (4, 3, 1), (5, 3, 1), (6, 3, 0), (7, 3, 1), (8, 3, 0), (9, 3, 1),
(0, 4, 1), (1, 4, 0), (2, 4, 1), (3, 4, 1), (4, 4, 1), (5, 4, 0), (6, 4, 1), (7, 4, 1), (8, 4, 0), (9, 4, 1),
(0, 5, 1), (1, 5, 1), (2, 5, 0), (3, 5, 0), (4, 5, 1), (5, 5, 0), (6, 5, 1), (7, 5, 0), (8, 5, 1), (9, 5, 1),
(0, 6, 0), (1, 6, 1), (2, 6, 1), (3, 6, 0), (4, 6, 1), (5, 6, 1), (6, 6, 1), (7, 6, 0), (8, 6, 1), (9, 6, 0),
(0, 7, 1), (1, 7, 0), (2, 7, 1), (3, 7, 1), (4, 7, 1), (5, 7, 0), (6, 7, 1), (7, 7, 1), (8, 7, 1), (9, 7, 1),
(0, 8, 1), (1, 8, 0), (2, 8, 0), (3, 8, 0), (4, 8, 1), (5, 8, 1), (6, 8, 0), (7, 8, 0), (8, 8, 0), (9, 8, 1),
(0, 9, 1), (1, 9, 1), (2, 9, 1), (3, 9, 1), (4, 9, 1), (5, 9, 0), (6, 9, 1), (7, 9, 1), (8, 9, 1), (9, 9, 1)
]

W, H = 10, 10
grid = {(x,y): z for (x,y,z) in maze}

start, end = (0,0), (9,9)

if grid[start] == 0 or grid[end] == 0:
    raise ValueError("No valid start/end")

# BFS Solver
def bfs(start, end):
    q = deque([start])
    parent = {start: None}
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        x,y = q.popleft()
        if (x,y) == end:
            break
        for dx,dy in moves:
            nx,ny = x+dx, y+dy
            if 0 <= nx < W and 0 <= ny < H and grid[(nx,ny)] == 1 and (nx,ny) not in parent:
                parent[(nx,ny)] = (x,y)
                q.append((nx,ny))
    if end not in parent:
        return None
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]

# A* Solver
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, end):
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start,end), 0, start))
    parent = {start: None}
    g_score = {start: 0}
    moves = [(1,0),(-1,0),(0,1),(0,-1)]

    while open_heap:
        _, g, cur = heapq.heappop(open_heap)

        if cur == end:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]

        x,y = cur
        for dx,dy in moves:
            nx,ny = x+dx, y+dy
            nxt = (nx,ny)
            if 0 <= nx < W and 0 <= ny < H and grid[nxt] == 1:
                newg = g + 1
                if nxt not in g_score or newg < g_score[nxt]:
                    g_score[nxt] = newg
                    parent[nxt] = cur
                    heapq.heappush(open_heap, (newg+heuristic(nxt,end), newg, nxt))
    return None

# Render
def render(name, path):
    print(f"\n{name}")
    print("Path length:", len(path) if path else 0)
    print("Path:", path)

    path_set = set(path or [])
    for y in range(H):
        row = []
        for x in range(W):
            if (x,y)==start: row.append('S')
            elif (x,y)==end: row.append('E')
            elif grid[(x,y)] == 0: row.append('0')
            elif (x,y) in path_set: row.append('*')
            else: row.append('1')
        print(' '.join(row))

# Time BFS
t0 = time.perf_counter()
path_bfs = bfs(start, end)
t1 = time.perf_counter()

# Time A*
t2 = time.perf_counter()
path_as = astar(start, end)
t3 = time.perf_counter()

# Output BFS
render("BFS", path_bfs)
print(f"BFS Runtime: {(t1 - t0)*1000:.5f} ms")
print("BFS Time Complexity:  O(V + E)  → In grid ~ O(W*H)")
print("BFS Space Complexity: O(V)      → Stores visited & queue\n")

# Output A*
render("A*", path_as)
print(f"A* Runtime: {(t3 - t2)*1000:.5f} ms")
print("A* Time Complexity (worst): O(V + E)")
print("A* Space Complexity:       O(V)")
print("With a good heuristic:     Much fewer nodes expanded, closer to optimal path length growth")
