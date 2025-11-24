import random
import time
import os
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


def simulate_game(weights, max_pieces: int = 200, record_steps: bool = False):
    """
    If record_steps is False: return total_lines.
    If record_steps is True: return (total_lines, list_of_board_states).
    """
    board = create_board()
    total_lines = 0
    steps = []

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

        if record_steps:
            steps.append(copy_board(board))

    if record_steps:
        return total_lines, steps
    return total_lines


# Simple text render

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def render_board(board: Board, generation=None, total_lines=None):
    clear_console()
    if generation is not None:
        print(f"Generation: {generation}")
    if total_lines is not None:
        print(f"Lines cleared (for this visual run): {total_lines}")
    print("+" + "-" * WIDTH + "+")
    for row in board:
        line = "".join("#" if c else "." for c in row)
        print("|" + line + "|")
    print("+" + "-" * WIDTH + "+")


def visual_game(weights, generation=None, max_pieces: int = 60, delay: float = 0.05):
    total_lines, steps = simulate_game(weights, max_pieces=max_pieces, record_steps=True)
    lines_so_far = 0
    for board in steps:
        render_board(board, generation=generation, total_lines=lines_so_far)
        time.sleep(delay)
        # just for basic feedback, recompute lines in this board
        # a bit rough but fine for visual
        full_rows = sum(1 for row in board if all(row))
        lines_so_far = full_rows
    render_board(board, generation=generation, total_lines=total_lines)
    print("\nVisual run finished. Press Ctrl+C to abort future runs if it is too slow.")
    time.sleep(1.0)


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
        child[key] = w1[key] if random.random() < 0.5 else w2[key]
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
    generations=30,
    elite_size=4,
    mutation_rate=0.2,
    games_per_individual=3,
    visual_every=5,
    visual_max_pieces=60,
):
    population = [random_weights() for _ in range(population_size)]

    for gen in range(generations):
        fitnesses = evaluate_population(population, games_per_individual=games_per_individual)
        paired = list(zip(population, fitnesses))
        paired.sort(key=lambda x: x[1], reverse=True)
        population = [p for p, f in paired]
        fitnesses = [f for p, f in paired]

        best_fit = fitnesses[0]
        best_weights = population[0]

        print("=" * 60)
        print(f"Generation {gen}")
        print(f"Population size (children count): {population_size}")
        print(f"Best fitness: {best_fit:.2f}")
        print(f"Best weights: {best_weights}")

        # Visual run for best child every visual_every generations
        if visual_every is not None and gen % visual_every == 0:
            try:
                visual_game(best_weights, generation=gen, max_pieces=visual_max_pieces, delay=0.05)
            except KeyboardInterrupt:
                print("Visual interrupted by user, continuing evolution without visual.")
                visual_every = None

        # Create next generation
        new_pop = population[:elite_size]
        while len(new_pop) < population_size:
            parent1 = random.choice(population[: population_size // 2])
            parent2 = random.choice(population[: population_size // 2])
            child = crossover_weights(parent1, parent2)
            child = mutate_weights(child, rate=mutation_rate)
            new_pop.append(child)
        population = new_pop

    fitnesses = evaluate_population(population, games_per_individual=games_per_individual)
    paired = list(zip(population, fitnesses))
    paired.sort(key=lambda x: x[1], reverse=True)
    best_weights, best_fit = paired[0]
    print("=" * 60)
    print("Training finished.")
    print("Best weights:", best_weights)
    print("Best fitness:", best_fit)
    return best_weights


if __name__ == "__main__":
    # Tune these if you want more madness
    BEST = run_evolution(
        population_size=30,
        generations=30,
        elite_size=4,
        mutation_rate=0.25,
        games_per_individual=3,
        visual_every=3,        # set to 1 to see every generation
        visual_max_pieces=60,  # how long each visual game runs
    )

    print("\nFinal visual run with best found weights...")
    time.sleep(2)
    visual_game(BEST, generation="FINAL", max_pieces=80, delay=0.05)
