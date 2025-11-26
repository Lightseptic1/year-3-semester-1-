import random
from typing import List, Tuple, Dict, Any

import numpy as np

WIDTH = 10
HEIGHT = 20

LINE_CLEAR_BONUS_SINGLE = 40.0
LINE_CLEAR_BONUS_DOUBLE = 200.0
LINE_CLEAR_BONUS_TRIPLE = 800.0
LINE_CLEAR_BONUS_TETRIS = 3000.0

TOP_OUT_PENALTY = -1000.0       

NN_INPUT_SIZE = 6
NN_HIDDEN_SIZE = 16
NN_OUTPUT_SIZE = 1

GENOME_SIZE = (
    NN_HIDDEN_SIZE * NN_INPUT_SIZE  # W1
    + NN_HIDDEN_SIZE                # b1
    + NN_OUTPUT_SIZE * NN_HIDDEN_SIZE  # W2
    + NN_OUTPUT_SIZE                # b2
)

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
                total += 3
    return total
HOLES_SCALE = 5.0
def extract_features(board: Board, lines_cleared: int) -> List[float]:
    """
    Compute a simple feature vector from the board and the
    current move outcome. Those features go into the neural net.
    """
    bumpiness, agg_height = bumpiness_and_aggregate_height(board)
    holes = count_holes(board) * HOLES_SCALE
    wells = total_well_depth(board)

    max_height = 0
    for x in range(WIDTH):
        h_col = 0
        for y in range(HEIGHT):
            if board[y][x]:
                h_col = HEIGHT - y
                break
        if h_col > max_height:
            max_height = h_col

    # features:
    # 0: lines cleared by this move
    # 1: aggregate column height
    # 2: holes
    # 3: bumpiness
    # 4: well depth
    # 5: maximum height of any column
    return [
        float(lines_cleared),
        float(agg_height),
        float(holes),
        float(bumpiness),
        float(wells),
        float(max_height),
    ]


def unpack_genome(genome: List[float]):
    """
    Convert flat genome into (W1, b1, W2, b2).
    """
    if len(genome) != GENOME_SIZE:
        raise ValueError(f"Genome length {len(genome)} != expected {GENOME_SIZE}")

    g = np.asarray(genome, dtype=np.float32)
    idx = 0

    # W1
    w1_size = NN_HIDDEN_SIZE * NN_INPUT_SIZE
    W1 = g[idx:idx + w1_size].reshape(NN_HIDDEN_SIZE, NN_INPUT_SIZE)
    idx += w1_size

    # b1
    b1 = g[idx:idx + NN_HIDDEN_SIZE]
    idx += NN_HIDDEN_SIZE

    # W2
    w2_size = NN_OUTPUT_SIZE * NN_HIDDEN_SIZE
    W2 = g[idx:idx + w2_size].reshape(NN_OUTPUT_SIZE, NN_HIDDEN_SIZE)
    idx += w2_size

    # b2
    b2 = g[idx:idx + NN_OUTPUT_SIZE]

    return W1, b1, W2, b2


def nn_forward(features: List[float], genome: List[float]) -> float:
    """
    One forward pass through the small neural net.
    """
    x = np.asarray(features, dtype=np.float32)  # shape (NN_INPUT_SIZE,)
    W1, b1, W2, b2 = unpack_genome(genome)

    # hidden layer with ReLU
    h = W1 @ x + b1
    h = np.maximum(h, 0.0)

    # output layer (linear)
    out = W2 @ h + b2
    return float(out[0])


def evaluate_board(board: Board, lines_cleared: int, genome: List[float]) -> float:
    """
    Score a resulting board after dropping one piece.
    Now uses a neural network whose parameters are given by genome.
    """
    features = extract_features(board, lines_cleared)
    return nn_forward(features, genome)


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
    genome: List[float],
    max_pieces: int = 200,
    record_steps: bool = False,
):
    """
    If record_steps is False:
        returns: fitness (Tetris score - top out penalty if any)
    If record_steps is True:
        returns: (total_score, list_of_(board,lines_so_far), topped_out_flag)

    The neural net encoded by genome chooses the best move at each step.
    """
    board = create_board()
    total_lines = 0
    total_score = 0.0
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

        # choose best move
        for new_board, lines_cleared, x, rot in moves:
            score = evaluate_board(new_board, lines_cleared, genome)
            if best_score is None or score > best_score:
                best_score = score
                best_board = new_board
                best_lines = lines_cleared
                best_x = x
                best_rot_index = rot

        if record_steps:
            rotation = TETROMINOES[shape_name][best_rot_index]
            piece_id = PIECE_IDS[shape_name]

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
            total_score += tetris_line_score(lines_cleared)

            # record post clear board as an extra frame with updated total_lines
            steps.append((copy_board(board), total_lines))
        else:
            # fast path, no animation
            board = best_board
            total_lines += best_lines
            total_score += tetris_line_score(best_lines)

    if record_steps:
        # return score for this run, not lines
        return total_score, steps, topped_out

    # Fitness for GA: based on Tetris score and a penalty if we top out
    fitness = float(total_score)
    if topped_out:
        fitness += TOP_OUT_PENALTY
    return fitness


def random_weights() -> List[float]:
    """
    Create a random neural network genome.
    The visualizer still calls this function by name,
    so we keep the name but it now returns a genome vector.
    """
    return [random.uniform(-1.0, 1.0) for _ in range(GENOME_SIZE)]


def mutate_weights(genome: List[float], rate: float = 0.1, scale: float = 0.5) -> List[float]:
    new = genome[:]
    for i in range(len(new)):
        if random.random() < rate:
            new[i] += random.uniform(-scale, scale)
    return new


def crossover_weights(g1: List[float], g2: List[float]) -> List[float]:
    child = []
    for a, b in zip(g1, g2):
        child.append(a if random.random() < 0.5 else b)
    return child


def evaluate_population(
    population: List[List[float]],
    games_per_individual: int = 3,
) -> List[float]:
    fitnesses: List[float] = []
    for genome in population:
        total = 0.0
        for _ in range(games_per_individual):
            total += float(simulate_game(genome))
        fitnesses.append(total / games_per_individual)
    return fitnesses


def evolve_one_generation(
    population: List[List[float]],
    elite_size: int = 4,
    mutation_rate: float = 0.15,
    games_per_individual: int = 3,
    global_best_weights: List[float] | None = None,
) -> Tuple[List[List[float]], Dict[str, Any]]:
    population_size = len(population)
    fitnesses = evaluate_population(population, games_per_individual=games_per_individual)
    paired = list(zip(population, fitnesses))
    paired.sort(key=lambda x: x[1], reverse=True)

    sorted_population = [p for p, f in paired]
    sorted_fitnesses = [f for p, f in paired]

    best_weights = sorted_population[0]
    best_fitness = sorted_fitnesses[0]

    # start next generation with elites from this generation
    new_pop: List[List[float]] = sorted_population[:elite_size]

    # if we have a global best from previous generations, force it into the population
    if global_best_weights is not None:
        # make sure we actually place a copy so we never mutate the stored one
        new_pop[0] = global_best_weights.copy()

    # rest are children from top half
    while len(new_pop) < population_size:
        parent1 = random.choice(sorted_population[: population_size // 2])
        parent2 = random.choice(sorted_population[: population_size // 2])
        child = crossover_weights(parent1, parent2)
        child = mutate_weights(child, rate=mutation_rate)
        new_pop.append(child)

    stats: Dict[str, Any] = {
        "best_weights": best_weights,         # now a genome vector
        "best_fitness": best_fitness,
        "sorted_population": sorted_population,
        "sorted_fitnesses": sorted_fitnesses,
    }
    return new_pop, stats
