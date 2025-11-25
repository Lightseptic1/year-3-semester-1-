import random
from typing import List, Tuple, Dict, Any

WIDTH = 10
HEIGHT = 20

# =========================
# SCORING / REWARD CONSTANTS
# =========================
# These control how the heuristic evaluates a single move / board.
# You can just change these numbers without touching code below.

# How strongly each feature interacts with the learned weights
SCORE_LINES_MULTIPLIER = 1.0
SCORE_HEIGHT_MULTIPLIER = 0.3
SCORE_HOLES_MULTIPLIER = 1.0
SCORE_BUMPINESS_MULTIPLIER = 0.4

# Extra bonuses for clearing lines (classic Tetris style)
LINE_CLEAR_BONUS_SINGLE = 40.0
LINE_CLEAR_BONUS_DOUBLE = 120.0
LINE_CLEAR_BONUS_TRIPLE = 400.0
LINE_CLEAR_BONUS_TETRIS = 2000.0

# Penalty when a move clears no lines
NO_LINE_PENALTY = 1.0  # subtract this from score

# Penalty for building too high
SAFE_HEIGHT = 15                # rows; above this is "too tall"
HEIGHT_PENALTY_PER_ROW = 1.5   # per row above SAFE_HEIGHT

# Fitness-level constants (whole game, not individual moves)
LINES_FITNESS_SCALE = 1.0       # how much each cleared line is worth
TOP_OUT_PENALTY = -1000.0       # huge negative when board tops out (no moves)

# =========================
# TETRIS DEFINITIONS
# =========================

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
PIECE_IDS = {
    "I": 1,
    "O": 2,
    "T": 3,
    "S": 4,
    "Z": 5,
    "J": 6,
    "L": 7,
}

Board = List[List[int]]


def create_board() -> Board:
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def copy_board(board: Board) -> Board:
    return [row[:] for row in board]


def collision(board: Board, shape, offset_x: int, offset_y: int) -> bool:
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


def lock_piece(board: Board, shape, offset_x: int, offset_y: int, piece_id: int) -> Tuple[Board, int]:
    new_board = copy_board(board)
    for x, y in shape:
        bx = x + offset_x
        by = y + offset_y
        if 0 <= by < HEIGHT and 0 <= bx < WIDTH:
            new_board[by][bx] = piece_id
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

def tetris_line_score(lines_cleared: int) -> float:
    """
    Classic style Tetris scoring for a single piece placement,
    based only on how many lines were cleared.
    """
    bonus_map = {
        1: LINE_CLEAR_BONUS_SINGLE,
        2: LINE_CLEAR_BONUS_DOUBLE,
        3: LINE_CLEAR_BONUS_TRIPLE,
        4: LINE_CLEAR_BONUS_TETRIS,
    }
    return bonus_map.get(lines_cleared, 0.0)

def evaluate_board(board: Board, lines_cleared: int, weights: Dict[str, float]) -> float:
    """
    Score a resulting board after dropping one piece.
    Uses both:
      - learned weights (GA)
      - hard-coded constants at the top
    """
    bumpiness, agg_height = bumpiness_and_aggregate_height(board)
    holes = count_holes(board)
    wells = total_well_depth(board)
    # base weighted sum
    score = 0.0
    score += SCORE_LINES_MULTIPLIER * weights["lines"] * lines_cleared
    score += SCORE_HEIGHT_MULTIPLIER * weights["height"] * agg_height
    score += SCORE_HOLES_MULTIPLIER * weights["holes"] * holes
    score += SCORE_BUMPINESS_MULTIPLIER * weights["bumpiness"] * bumpiness
    score += 1.0 * weights["wells"] * wells
    # shaped bonus for line clears
    if lines_cleared > 0:
        bonus_map = {
            1: LINE_CLEAR_BONUS_SINGLE,
            2: LINE_CLEAR_BONUS_DOUBLE,
            3: LINE_CLEAR_BONUS_TRIPLE,
            4: LINE_CLEAR_BONUS_TETRIS,
        }
        score += bonus_map.get(lines_cleared, 0.0)
    else:
        score -= NO_LINE_PENALTY

    # penalty for being too tall
    max_height = 0
    for x in range(WIDTH):
        h_col = 0
        for y in range(HEIGHT):
            if board[y][x]:
                h_col = HEIGHT - y
                break
        if h_col > max_height:
            max_height = h_col

    if max_height > SAFE_HEIGHT:
        score -= HEIGHT_PENALTY_PER_ROW * (max_height - SAFE_HEIGHT)

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
            piece_id = PIECE_IDS[shape_name]
            new_board, lines_cleared = lock_piece(board, rotation, x, y, piece_id)
            results.append((new_board, lines_cleared, x, rot_index))
    return results
def simulate_game(
    weights: Dict[str, float],
    max_pieces: int = 200,
    record_steps: bool = False,
):
    """
    If record_steps is False:
        returns: fitness (Tetris score - top out penalty if any)
    If record_steps is True:
        returns: (total_score, list_of_(board,lines_so_far), topped_out_flag)
    """
    board = create_board()
    total_lines = 0
    total_score = 0.0          # NEW: Tetris style score
    steps: List[Tuple[Board, int]] = []
    topped_out = False

    for _ in range(max_pieces):
        shape_name = random.choice(SHAPES)
        moves = all_possible_moves(board, shape_name)

        # no legal placements, game over
        if not moves:
            topped_out = True
            break

        best_score = None
        best_board = None
        best_lines = 0
        best_x = 0
        best_rot_index = 0

        # choose best move (still uses heuristic evaluate_board)
        for new_board, lines_cleared, x, rot in moves:
            score = evaluate_board(new_board, lines_cleared, weights)
            if best_score is None or score > best_score:
                best_score = score
                best_board = new_board
                best_lines = lines_cleared
                best_x = x
                best_rot_index = rot

        if record_steps:
            rotation = TETROMINOES[shape_name][best_rot_index]
            piece_id = PIECE_IDS[shape_name]

            # recompute landing y for chosen move
            y = 0
            while not collision(board, rotation, best_x, y):
                y += 1
            y -= 1
            if y < 0:
                topped_out = True
                break

            # fall animation from top to landing row
            for anim_y in range(y + 1):
                temp_board = copy_board(board)
                for px, py in rotation:
                    bx = best_x + px
                    by = anim_y + py
                    if 0 <= bx < WIDTH and 0 <= by < HEIGHT:
                        temp_board[by][bx] = piece_id
                # record board plus current total_lines (no new lines yet)
                steps.append((temp_board, total_lines))

            # now actually lock the piece and clear lines
            locked_board, lines_cleared = lock_piece(board, rotation, best_x, y, piece_id)
            board = locked_board
            total_lines += lines_cleared
            total_score += tetris_line_score(lines_cleared)   # NEW: update score

            # record post clear board as an extra frame with updated total_lines
            steps.append((copy_board(board), total_lines))
        else:
            # fast path, no animation
            board = best_board
            total_lines += best_lines
            total_score += tetris_line_score(best_lines)       # NEW: update score

    if record_steps:
        # return score for this run, not lines
        return total_score, steps, topped_out

    # Fitness for GA: now based on Tetris score
    fitness = float(total_score)
    if topped_out:
        fitness += TOP_OUT_PENALTY
    return fitness

# =========================
# GENETIC ALGORITHM HELPERS
# =========================
def total_well_depth(board: Board) -> int:
    """
    Compute a simple measure of how deep vertical wells are.
    A well cell is an empty cell whose left and right neighbors
    are both filled (or off board at the edges).
    We sum over all such cells.
    """
    total = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if board[y][x] != 0:
                continue

            left_filled = (x == 0) or (board[y][x - 1] != 0)
            right_filled = (x == WIDTH - 1) or (board[y][x + 1] != 0)

            if left_filled and right_filled:
                total += 1
    return total

def random_weights() -> Dict[str, float]:
    # Initial ranges. You can change these to bias evolution.
    return {
        "lines": random.uniform(0.0, 6.0),
        "height": random.uniform(-0.7, 0.2),
        "holes": random.uniform(-5.0, -0.5),
        "bumpiness": random.uniform(-0.7, 0.2),
        "wells": random.uniform(0.0, 3.0),
    }


def mutate_weights(weights: Dict[str, float], rate: float = 0.1, scale: float = 0.5) -> Dict[str, float]:
    new = weights.copy()
    for key in new:
        if random.random() < rate:
            new[key] += random.uniform(-scale, scale)
    return new


def crossover_weights(w1: Dict[str, float], w2: Dict[str, float]) -> Dict[str, float]:
    child = {}
    for key in w1:
        child[key] = w1[key] if random.random() < 0.5 else w2[key]
    return child


def evaluate_population(
    population: List[Dict[str, float]],
    games_per_individual: int = 3,
) -> List[float]:
    fitnesses: List[float] = []
    for w in population:
        total = 0.0
        for _ in range(games_per_individual):
            total += float(simulate_game(w))
        fitnesses.append(total / games_per_individual)
    return fitnesses


def evolve_one_generation(
    population: List[Dict[str, float]],
    elite_size: int = 4,
    mutation_rate: float = 0.15,
    games_per_individual: int = 3,
) -> Tuple[List[Dict[str, float]], Dict[str, Any]]:
    population_size = len(population)
    fitnesses = evaluate_population(population, games_per_individual=games_per_individual)
    paired = list(zip(population, fitnesses))
    paired.sort(key=lambda x: x[1], reverse=True)

    sorted_population = [p for p, f in paired]
    sorted_fitnesses = [f for p, f in paired]

    best_weights = sorted_population[0]
    best_fitness = sorted_fitnesses[0]

    new_pop: List[Dict[str, float]] = sorted_population[:elite_size]
    # rest are children from top half
    while len(new_pop) < population_size:
        parent1 = random.choice(sorted_population[: population_size // 2])
        parent2 = random.choice(sorted_population[: population_size // 2])
        child = crossover_weights(parent1, parent2)
        child = mutate_weights(child, rate=mutation_rate)
        new_pop.append(child)

    stats: Dict[str, Any] = {
        "best_weights": best_weights,
        "best_fitness": best_fitness,
        "sorted_population": sorted_population,
        "sorted_fitnesses": sorted_fitnesses,
    }
    return new_pop, stats
