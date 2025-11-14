

import heapq
import time
from collections import deque


GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)  

GOAL_POS = {v: i for i, v in enumerate(GOAL)}

def neighbors_index():
    nbrs = {}
    for i in range(9):
        r, c = divmod(i, 3)
        opts = []
        if r > 0: opts.append(i - 3)
        if r < 2: opts.append(i + 3)
        if c > 0: opts.append(i - 1)
        if c < 2: opts.append(i + 1)
        nbrs[i] = opts
    return nbrs

NEIGH = neighbors_index()


def h_misplaced(state):
    # count tiles not in place (ignore blank)
    return sum(1 for i, v in enumerate(state) if v and v != GOAL[i])

def h_manhattan(state):
    # sum of Manhattan distances for all tiles (ignore blank)
    s = 0
    for i, v in enumerate(state):
        if v == 0:
            continue
        r, c = divmod(i, 3)
        gr, gc = divmod(GOAL_POS[v], 3)
        s += abs(r - gr) + abs(c - gc)
    return s

def h_linear_conflict(state):
    """
    Linear conflict = Manhattan + 2 * (# of linear conflicts)
    A linear conflict occurs when two tiles are in their goal row (or column)
    but reversed relative to their goal order, so they must cross.
    This is admissible and consistent for the 8-puzzle.
    """
    man = h_manhattan(state)

    # row conflicts
    conflicts = 0
    for r in range(3):
        row_vals = [state[3*r + c] for c in range(3)]
        # tiles that belong in this row by goal row
        goal_cols_seq = []
        for v in row_vals:
            if v != 0 and (GOAL_POS[v] // 3) == r:
                goal_cols_seq.append(GOAL_POS[v] % 3)
        # count inversions in goal column sequence
        conflicts += count_inversions(goal_cols_seq)

    # column conflicts
    for c in range(3):
        col_vals = [state[r*3 + c] for r in range(3)]
        goal_rows_seq = []
        for v in col_vals:
            if v != 0 and (GOAL_POS[v] % 3) == c:
                goal_rows_seq.append(GOAL_POS[v] // 3)
        conflicts += count_inversions(goal_rows_seq)

    return man + 2 * conflicts

def count_inversions(seq):
    # small n, simple O(n^2) is fine
    inv = 0
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                inv += 1
    return inv

HEURISTICS = {
    "misplaced": h_misplaced,
    "manhattan": h_manhattan,
    "linear_conflict": h_linear_conflict
}


def is_solvable(state):
    arr = [v for v in state if v != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1

    return inv % 2 == 0


def astar(initial, hfunc):
    if initial == GOAL:
        return True, 0, 0, [initial]

    open_heap = []
    push_counter = 0
    g_score = {initial: 0}
    f0 = hfunc(initial)
    heapq.heappush(open_heap, (f0, 0, push_counter, initial))
    parent = {initial: None}
    visited = set()
    expanded = 0

    while open_heap:
        f, g, _, cur = heapq.heappop(open_heap)
        if cur in visited:
            continue
        visited.add(cur)
        expanded += 1

        if cur == GOAL:
            path = reconstruct_path(parent, cur)
            return True, len(path) - 1, expanded, path

        z = cur.index(0)
        for nxt_z in NEIGH[z]:
            nxt = list(cur)
            nxt[z], nxt[nxt_z] = nxt[nxt_z], nxt[z]
            nxt = tuple(nxt)
            newg = g + 1
            if newg < g_score.get(nxt, 10**9):
                g_score[nxt] = newg
                parent[nxt] = cur
                push_counter += 1
                heapq.heappush(open_heap, (newg + hfunc(nxt), newg, push_counter, nxt))

    return False, None, expanded, None

def reconstruct_path(parent, s):
    path = []
    while s is not None:
        path.append(s)
        s = parent[s]
    path.reverse()
    return path


TESTS = [
    ("S0_solved",      (1, 2, 3, 4, 5, 6, 7, 8, 0)),           
    ("S1_one_move",    (1, 2, 3, 4, 5, 6, 7, 0, 8)),             
    ("S2_two_moves",   (1, 2, 3, 4, 5, 6, 0, 7, 8)),             
    ("S3_hard_31",     (8, 6, 7, 2, 5, 4, 3, 0, 1)),             
    ("U1_unsolvable",  (2, 1, 6, 3, 8, 5, 7, 0, 4))           
]


def print_state(s):
    for r in range(3):
        print(s[3*r:3*r+3])

def main():
    for name, state in TESTS:
        print("=" * 50)
        print(f"Case: {name}")
        print("Initial state:")
        print_state(state)
        solv = is_solvable(state)
        print(f"Solvable: {solv}")

        for hname, hfunc in HEURISTICS.items():
            t0 = time.perf_counter()
            if solv:
                solved, moves, expanded, path = astar(state, hfunc)
            else:
                solved, moves, expanded, path = False, None, 0, None
            t1 = time.perf_counter()

            print(f"  Heuristic: {hname}")
            print(f"    Solved: {solved}")
            print(f"    Moves: {moves}")
            print(f"    Nodes expanded: {expanded}")
            print(f"    Time: {(t1 - t0) * 1000:.3f} ms")

            if solved and name in ("S0_solved", "S1_one_move", "S2_two_moves"):
                # show path only for the small cases to keep output manageable
                print("    Solution path:")
                for step in path:
                    print_state(step)
                    print("---")

if __name__ == "__main__":
    main()
