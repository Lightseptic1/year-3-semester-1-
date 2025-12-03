import random
from copy import deepcopy

WIDTH = 10
HEIGHT = 20

# ======== PIECE DEFINITIONS ========
# Each piece is a list of rotations
# Each rotation is a list of (x, y) block positions

TETROMINOS = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, -1), (1, 0), (1, 1), (1, 2)]
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    "T": [
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, -1), (0, 0), (1, 0), (1, 1)],
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(0, -1), (0, 0), (1, 0), (0, 1)]
    ],
    "L": [
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(2, -1), (0, 0), (1, 0), (2, 0)]
    ],
    "J": [
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, -1), (0, 0), (1, 0), (2, 0)],
        [(0, 0), (1, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0), (2, 1)]
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, -1), (0, 0), (1, 0), (1, 1)]
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, -1), (0, 0), (1, 0), (0, 1)]
    ],
}

PIECES = list(TETROMINOS.keys())


def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def in_bounds(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def check_collision(board, blocks, off_x, off_y):
    """Return True if piece with given offset collides or is out of bounds."""
    for (bx, by) in blocks:
        x = bx + off_x
        y = by + off_y
        if not in_bounds(x, y):
            return True
        if board[y][x] != 0:
            return True
    return False


def lock_piece(board, blocks, off_x, off_y, value):
    """Place piece blocks into the board with given value."""
    new_board = deepcopy(board)
    for (bx, by) in blocks:
        x = bx + off_x
        y = by + off_y
        if in_bounds(x, y):
            new_board[y][x] = value
    return new_board


def clear_full_lines(board):
    """Remove complete lines and return new board and number of lines cleared."""
    new_board = []
    cleared = 0
    for row in board:
        if all(cell != 0 for cell in row):
            cleared += 1
        else:
            new_board.append(row)
    # Add empty rows at the top
    while len(new_board) < HEIGHT:
        new_board.insert(0, [0 for _ in range(WIDTH)])
    return new_board, cleared


# ======== FEATURE COMPUTATION ========

def column_heights(board):
    heights = [0] * WIDTH
    for x in range(WIDTH):
        h = 0
        for y in range(HEIGHT):
            if board[y][x] != 0:
                h = HEIGHT - y
                break
        heights[x] = h
    return heights


def count_holes(board):
    """Holes = empty cells that have at least one filled cell above them in the same column."""
    holes = 0
    for x in range(WIDTH):
        seen_block = False
        for y in range(HEIGHT):
            if board[y][x] != 0:
                seen_block = True
            elif seen_block and board[y][x] == 0:
                holes += 1
    return holes


def bumpiness_and_agg_height(heights):
    agg_height = sum(heights)
    bumpiness = 0
    for x in range(WIDTH - 1):
        bumpiness += abs(heights[x] - heights[x + 1])
    return bumpiness, agg_height


def evaluate_board(board, lines_cleared):
    """
    Simple heuristic score.
    Higher is better.
    We want:
      more lines cleared
      fewer holes
      lower aggregate height
      lower bumpiness
    """
    heights = column_heights(board)
    holes = count_holes(board)
    bumpiness, agg_height = bumpiness_and_agg_height(heights)

    score = 0.0
    score += lines_cleared * 10.0      # clear lines good
    score -= holes * 5.0               # holes very bad
    score -= agg_height * 0.5          # tall board bad
    score -= bumpiness * 0.5           # uneven surface bad

    return score


# ======== MOVE GENERATION ========

def generate_all_moves(board, piece_id):
    """
    For a given board and current piece:
      Return list of (score, new_board, lines_cleared) for all legal placements.
    """
    results = []
    rotations = TETROMINOS[piece_id]

    for rot_index, blocks in enumerate(rotations):
        # Find horizontal range where piece can be placed
        # Find min and max x of blocks
        min_bx = min(bx for bx, _ in blocks)
        max_bx = max(bx for bx, _ in blocks)

        for x in range(-min_bx, WIDTH - max_bx):
            # Drop piece from top until it collides
            y = 0
            while True:
                if check_collision(board, blocks, x, y):
                    # Last valid position is one row above
                    final_y = y - 1
                    # If even one row above collides, this move is impossible
                    if final_y < 0 or check_collision(board, blocks, x, final_y):
                        break

                    temp_board = lock_piece(board, blocks, x, final_y, value=1)
                    temp_board, lines_cleared = clear_full_lines(temp_board)
                    score = evaluate_board(temp_board, lines_cleared)
                    results.append({
                        "score": score,
                        "board": temp_board,
                        "lines": lines_cleared,
                        "rot": rot_index,
                        "x": x,
                        "y": final_y,
                    })
                    break
                else:
                    y += 1
                    if y >= HEIGHT:
                        # Hit bottom
                        final_y = y - 1
                        temp_board = lock_piece(board, blocks, x, final_y, value=1)
                        temp_board, lines_cleared = clear_full_lines(temp_board)
                        score = evaluate_board(temp_board, lines_cleared)
                        results.append({
                            "score": score,
                            "board": temp_board,
                            "lines": lines_cleared,
                            "rot": rot_index,
                            "x": x,
                            "y": final_y,
                        })
                        break

    return results


def choose_best_move(board, piece_id):
    moves = generate_all_moves(board, piece_id)
    if not moves:
        return None
    best = max(moves, key=lambda m: m["score"])
    return best


# ======== GAME LOOP WITH HEURISTIC BOT ========

def run_one_game(max_steps=1000, print_every=0):
    board = create_board()
    total_lines = 0
    steps = 0

    while steps < max_steps:
        piece = random.choice(PIECES)
        move = choose_best_move(board, piece)
        if move is None:
            # no legal moves -> game over
            break

        board = move["board"]
        total_lines += move["lines"]
        steps += 1

        if print_every and steps % print_every == 0:
            print(f"After {steps} pieces, total lines: {total_lines}")

    return total_lines, board


def main():
    games = 10
    total = 0
    for i in range(games):
        lines, _ = run_one_game()
        print(f"Game {i + 1}: cleared {lines} lines")
        total += lines
    print(f"Average lines over {games} games: {total / games:.2f}")


if __name__ == "__main__":
    main()
