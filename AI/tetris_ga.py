import random
from typing import List, Tuple

WIDTH = 10
HEIGHT = 20

# Tetromino shapes: list of rotations, each rotation is list of (x, y) blocks
TETROMINOES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

SHAPES = list(TETROMINOES.keys())

Board = List[List[int]]


def create_board() -> Board:
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def copy_board(board: Board) -> Board:
    return [row[:] for row in board]


def collision(board: Board, shape: List[Tuple[int, int]], offset_x: int, offset_y: int) -> bool:
    for x, y in shape:
        bx = x + offset_x
        by = y + offset_y
        if bx < 0 or bx >= WIDTH or by < 0 or by >= HEIGHT:
            return True
        if board[by][bx]:
            return True
    return False


def clear_lines(board: Board) -> Tuple[Board, int]:
    new_rows = []
    cleared = 0
    for row in board:
        if all(row):
            cleared += 1
        else:
            new_rows.append(row)
    while len(new_rows) < HEIGHT:
        new_rows.insert(0, [0 for _ in range(WIDTH)])
    return new_rows, cleared


def lock_piece(board: Board, shape: List[Tuple[int, int]], offset_x: int, offset_y: int) -> Tuple[Board, int]:
    new_board = copy_board(board)
    for x, y in shape:
        bx = x + offset_x
        by = y + offset_y
        if 0 <= by < HEIGHT and 0 <= bx < WIDTH:
            new_board[by][bx] = 1
    new_board, lines_cleared = clear_lines(new_board)
    return new_board, lines_cleared


def count_holes(board: Board) -> int:
    holes = 0
    for x in range(WIDTH):
        block_seen = False
        for y in range(HEIGHT):
            if board[y][x]:
                block_seen = True
            elif block_seen and not board[y][x]:
                holes += 1
    return holes


def bumpiness_and_aggregate_height(board: Board) -> Tuple[int, int]:
    heights = []
    for x in range(WIDTH):
        h = 0
        for y in range(HEIGHT):
            if board[y][x]:
                h = HEIGHT - y
                break
        heights.append(h)
    aggregate_height = sum(heights)
    bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(WIDTH - 1))
    return bumpiness, aggregate_height


def evaluate_board(board: Board, lines_cleared: int, weights) -> float:
    # weights is dict with keys: lines, height, holes, bumpiness
    bumpiness, agg_height = bumpiness_and_aggregate_height(board)
    holes = count_holes(board)
    score = (
        weights["lines"] * lines_cleared
        + weights["height"] * agg_height
        + weights["holes"] * holes
        + weights["bumpiness"] * bumpiness
    )
    return score


def all_possible_moves(board: Board, shape_name: str):
    results = []
    rotations = TETROMINOES[shape_name]
    for rot_index, rotation in enumerate(rotations):
        min_x = min(x for x, y in rotation)
        max_x = max(x for x, y in rotation)
        for x in range(-min_x, WIDTH - max_x):
            y = 0
            while not collision(board, rotation, x, y):
                y += 1
            y -= 1
            if y < 0:
                continue
            new_board, lines_cleared = lock_piece(board, rotation, x, y)
            results.append((new_board, lines_cleared, x, rot_index))
    return results


def simulate_game(weights, max_pieces: int = 200) -> int:
    board = create_board()
    total_lines = 0
    for _ in range(max_pieces):
        shape_name = random.choice(SHAPES)
        moves = all_possible_moves(board, shape_name)
        if not moves:
            break
        best_score = None
        best_board = None
        best_lines = 0
        for new_board, lines_cleared, x, rot in moves:
            score = evaluate_board(new_board, lines_cleared, weights)
            if best_score is None or score > best_score:
                best_score = score
                best_board = new_board
                best_lines = lines_cleared
        board = best_board
        total_lines += best_lines
    return total_lines


# Genetic algorithm

def random_weights():
    return {
        "lines": random.uniform(-1.0, 1.0),
        "height": random.uniform(-1.0, 1.0),
        "holes": random.uniform(-1.0, 1.0),
        "bumpiness": random.uniform(-1.0, 1.0),
    }


def mutate_weights(weights, rate=0.1, scale=0.5):
    new = weights.copy()
    for key in new:
        if random.random() < rate:
            new[key] += random.uniform(-scale, scale)
    return new


def crossover_weights(w1, w2):
    child = {}
    for key in w1:
        if random.random() < 0.5:
            child[key] = w1[key]
        else:
            child[key] = w2[key]
    return child


def evaluate_population(population, games_per_individual=3):
    fitnesses = []
    for w in population:
        total = 0
        for _ in range(games_per_individual):
            total += simulate_game(w)
        fitnesses.append(total / games_per_individual)
    return fitnesses


def run_evolution(
    population_size=30,
    generations=20,
    elite_size=4,
    mutation_rate=0.2,
):
    population = [random_weights() for _ in range(population_size)]
    for gen in range(generations):
        fitnesses = evaluate_population(population)
        paired = list(zip(population, fitnesses))
        paired.sort(key=lambda x: x[1], reverse=True)
        population = [p for p, f in paired]
        fitnesses = [f for p, f in paired]
        best_fit = fitnesses[0]
        print(f"Generation {gen}: best fitness {best_fit:.2f}, weights {population[0]}")
        new_pop = population[:elite_size]
        while len(new_pop) < population_size:
            parent1 = random.choice(population[: population_size // 2])
            parent2 = random.choice(population[: population_size // 2])
            child = crossover_weights(parent1, parent2)
            child = mutate_weights(child, rate=mutation_rate)
            new_pop.append(child)
        population = new_pop
    fitnesses = evaluate_population(population)
    paired = list(zip(population, fitnesses))
    paired.sort(key=lambda x: x[1], reverse=True)
    best_weights, best_fit = paired[0]
    print("Best weights:", best_weights)
    print("Best fitness:", best_fit)
    return best_weights


if __name__ == "__main__":
    best = run_evolution()
