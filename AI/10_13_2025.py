from collections import deque
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

W = 10
H = 10
grid = {(x,y): z for (x,y,z) in maze}

start = (0,0)
end   = (9,9)

if grid.get(start,0) != 1 or grid.get(end,0) != 1:
    raise ValueError("No solution")

def bfs(start, end, grid, W, H):
    q = deque([start])
    parent = {start: None}
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        x,y = q.popleft()
        if (x,y) == end:
            break
        for dx,dy in moves:
            nx,ny = x+dx, y+dy
            if 0 <= nx < W and 0 <= ny < H and grid.get((nx,ny),0) == 1 and (nx,ny) not in parent:
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

path = bfs(start, end, grid, W, H)

print("Path length:", 0 if path is None else len(path))
print("Path:", path)

# optional: simple render
if path:
    path_set = set(path)
    for y in range(H):
        row = []
        for x in range(W):
            if (x,y) == start: row.append('S')
            elif (x,y) == end: row.append('E')
            elif grid[(x,y)] == 0: row.append('0')   # white/blocked
            elif (x,y) in path_set: row.append('*')  # on path
            else: row.append('1')                    # black/walkable
        print(' '.join(row))
