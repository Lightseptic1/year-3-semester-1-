import sys
import random
from copy import deepcopy

import pygame

pygame.init()

# ============ BASIC TETRIS CONFIG ============

WIDTH = 10
HEIGHT = 20

CELL_SIZE = 24
BOARD_PIXEL_W = WIDTH * CELL_SIZE
BOARD_PIXEL_H = HEIGHT * CELL_SIZE

WINDOW_W = 800
WINDOW_H = 640

BG_COLOR = (230, 230, 230)
BOARD_BG_COLOR = (255, 255, 255)
GRID_COLOR = (210, 210, 210)
BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (50, 50, 50)

PIECE_COLORS = {
    0: (255, 255, 255),
    1: (0, 255, 255),    # I
    2: (255, 255, 0),    # O
    3: (160, 0, 240),    # T
    4: (0, 0, 255),      # J
    5: (255, 165, 0),    # L
    6: (0, 255, 0),      # S
    7: (255, 0, 0),      # Z
}

# piece blocks defined as rotations of (x, y)
TETROMINOS = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, -1), (1, 0), (1, 1), (1, 2)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, -1), (0, 0), (1, 0), (1, 1)],
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(0, -1), (0, 0), (1, 0), (0, 1)],
    ],
    "L": [
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(2, -1), (0, 0), (1, 0), (2, 0)],
    ],
    "J": [
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, -1), (0, 0), (1, 0), (2, 0)],
        [(0, 0), (1, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, -1), (0, 0), (1, 0), (0, 1)],
    ],
}

PIECES = list(TETROMINOS.keys())
PIECE_ID_BY_NAME = {
    "I": 1,
    "O": 2,
    "T": 3,
    "J": 4,
    "L": 5,
    "S": 6,
    "Z": 7,
}

# positions
BOARD_X = (WINDOW_W - BOARD_PIXEL_W) // 2
BOARD_Y = 80

HOLD_BOX_W = 160
HOLD_BOX_H = 120
HOLD_BOX_X = BOARD_X - HOLD_BOX_W - 40
HOLD_BOX_Y = 120

NEXT_BOX_W = 160
NEXT_BOX_H = 120
NEXT_BOX_X = BOARD_X + BOARD_PIXEL_W + 40
NEXT_BOX_Y = 120

TITLE_FONT = pygame.font.SysFont("consolas", 40, bold=True)
LABEL_FONT = pygame.font.SysFont("consolas", 24, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 18)

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Tetris AI vs Board")

# ============ GAME STATE ============

def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def in_bounds(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def check_collision(board, blocks, off_x, off_y):
    for bx, by in blocks:
        x = bx + off_x
        y = by + off_y
        if not in_bounds(x, y):
            return True
        if board[y][x] != 0:
            return True
    return False


def lock_piece(board, blocks, off_x, off_y, value):
    new_board = deepcopy(board)
    for bx, by in blocks:
        x = bx + off_x
        y = by + off_y
        if in_bounds(x, y):
            new_board[y][x] = value
    return new_board


def clear_full_lines(board):
    new_board = []
    cleared = 0
    for row in board:
        if all(cell != 0 for cell in row):
            cleared += 1
        else:
            new_board.append(row)
    while len(new_board) < HEIGHT:
        new_board.insert(0, [0 for _ in range(WIDTH)])
    return new_board, cleared


# ============ OLD FEATURE HELPERS (unused, can be deleted if you want) ============

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


# ============ NEW: IMPORT NN BRAIN FROM CORE ============

from tetris_ga_core import extract_features, nn_forward, GENOME_SIZE

# Paste the comma separated weights line from tetris_ga_core here
BEST_GENOME = [ 0.145382,0.291226,0.313767,-0.551176,-0.429694,0.325739,-0.832168,0.033023,0.409152,0.013712,0.777361,0.894846,-0.901696,-0.961656,-0.325251,0.952102,0.918507,-0.638032,0.487808,0.132146,-0.474255,-0.142439,-0.770881,-0.632562,-0.872946,0.243297,-0.696962,-0.531384,0.787158,-0.848989,-0.248189,0.502548,0.771462,-0.354661,0.135969,0.157457,0.743376,0.726586,-0.915427,0.246236,-0.347233,0.175947,0.319230,-0.210424,-0.278844,-0.547499,-0.938187,0.956221,0.872963,-0.822175,0.648234,0.242929,0.013054,-0.653908,0.328202,0.205582,0.429925,0.105460,0.697134,-0.512046,-0.500270,-0.610313,0.169110,-0.655654,0.049515,-0.375854,0.620891,0.567360,-0.919748,-0.551674,0.122384,-0.759842,0.274231,0.596166,0.770688,0.616712,0.567558,-0.196622,0.307246,-0.774766,0.332871,-0.584247,-0.935652,-0.769148,0.845647,-0.553104,0.854773,-0.297836,0.447659,0.566526,-0.444110,0.349057,0.548177,0.273105,0.453248,-0.011311,0.610179,-0.916403,-0.704529,0.704783,0.384690,0.318844,0.712302,-0.111777,-0.527124,-0.813341,0.467319,-0.614544,-0.231453,0.573860,-0.684907,-0.628883,0.297037,0.151755,-0.582446,-0.062092,0.479359,-0.767793,0.574844,0.719481,-0.841273,0.938980,-0.833825,0.453501,-0.970720,0.854998,-0.524372,-0.717943,-0.000869
]

# Optional safety check so you know the paste is correct
if BEST_GENOME:
    assert len(BEST_GENOME) == GENOME_SIZE, (
        f"BEST_GENOME has length {len(BEST_GENOME)}, "
        f"but GENOME_SIZE is {GENOME_SIZE}"
    )

def evaluate_board(board, lines_cleared):
    """
    Use the evolved neural net (BEST_GENOME) to score this board position.
    """
    feats = extract_features(board, lines_cleared)
    return nn_forward(feats, BEST_GENOME)


# ============ AI MOVE GENERATION ============

def generate_all_moves(board, piece_name):
    results = []
    rotations = TETROMINOS[piece_name]

    for rot_index, blocks in enumerate(rotations):
        min_bx = min(bx for bx, _ in blocks)
        max_bx = max(bx for bx, _ in blocks)

        for x in range(-min_bx, WIDTH - max_bx):
            y = 0
            while True:
                if check_collision(board, blocks, x, y):
                    final_y = y - 1
                    if final_y < 0 or check_collision(board, blocks, x, final_y):
                        break
                    temp_board = lock_piece(board, blocks, x, final_y,
                                            PIECE_ID_BY_NAME[piece_name])
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
                        final_y = y - 1
                        temp_board = lock_piece(board, blocks, x, final_y,
                                                PIECE_ID_BY_NAME[piece_name])
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


def choose_best_move(board, piece_name):
    moves = generate_all_moves(board, piece_name)
    if not moves:
        return None
    return max(moves, key=lambda m: m["score"])


# ============ DRAWING ============

def draw_board(surface, board):
    pygame.draw.rect(
        surface,
        BORDER_COLOR,
        (BOARD_X - 2, BOARD_Y - 2, BOARD_PIXEL_W + 4, BOARD_PIXEL_H + 4),
        2,
    )
    pygame.draw.rect(
        surface,
        BOARD_BG_COLOR,
        (BOARD_X, BOARD_Y, BOARD_PIXEL_W, BOARD_PIXEL_H),
    )

    for x in range(WIDTH + 1):
        px = BOARD_X + x * CELL_SIZE
        pygame.draw.line(
            surface, GRID_COLOR, (px, BOARD_Y), (px, BOARD_Y + BOARD_PIXEL_H)
        )
    for y in range(HEIGHT + 1):
        py = BOARD_Y + y * CELL_SIZE
        pygame.draw.line(
            surface, GRID_COLOR, (BOARD_X, py), (BOARD_X + BOARD_PIXEL_W, py)
        )

    for y in range(HEIGHT):
        for x in range(WIDTH):
            val = board[y][x]
            if val != 0:
                color = PIECE_COLORS.get(val, (0, 0, 0))
                rect = pygame.Rect(
                    BOARD_X + x * CELL_SIZE,
                    BOARD_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


# simple 4x4 draw for hold/next display
TETROMINO_SHAPES_4X4 = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(1, 1), (2, 1), (1, 2), (2, 2)],
    "T": [(1, 1), (0, 2), (1, 2), (2, 2)],
    "J": [(0, 1), (0, 2), (1, 2), (2, 2)],
    "L": [(2, 1), (0, 2), (1, 2), (2, 2)],
    "S": [(1, 1), (2, 1), (0, 2), (1, 2)],
    "Z": [(0, 1), (1, 1), (1, 2), (2, 2)],
}

def draw_piece_box(surface, title, box_x, box_y, box_w, box_h, piece_name):
    pygame.draw.rect(surface, BORDER_COLOR, (box_x, box_y, box_w, box_h), 4)

    label = LABEL_FONT.render(title, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(box_x + box_w // 2, box_y - 15))
    surface.blit(label, label_rect)

    grid_size = CELL_SIZE
    inner_w = 4 * grid_size
    inner_h = 4 * grid_size
    inner_x = box_x + (box_w - inner_w) // 2
    inner_y = box_y + (box_h - inner_h) // 2

    pygame.draw.rect(surface, BOARD_BG_COLOR,
                     (inner_x, inner_y, inner_w, inner_h))
    pygame.draw.rect(surface, BORDER_COLOR,
                     (inner_x, inner_y, inner_w, inner_h), 2)

    for i in range(5):
        pygame.draw.line(surface, GRID_COLOR,
                         (inner_x + i * grid_size, inner_y),
                         (inner_x + i * grid_size, inner_y + inner_h))
        pygame.draw.line(surface, GRID_COLOR,
                         (inner_x, inner_y + i * grid_size),
                         (inner_x + inner_w, inner_y + i * grid_size))

    if piece_name and piece_name in TETROMINO_SHAPES_4X4:
        blocks = TETROMINO_SHAPES_4X4[piece_name]
        color = PIECE_COLORS[PIECE_ID_BY_NAME[piece_name]]
        for bx, by in blocks:
            rect = pygame.Rect(
                inner_x + bx * grid_size,
                inner_y + by * grid_size,
                grid_size,
                grid_size,
            )
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def draw_score(surface, score):
    label = TITLE_FONT.render(f"SCORE: {score}", True, TEXT_COLOR)
    rect = label.get_rect(center=(WINDOW_W // 2, 40))
    surface.blit(label, rect)


def draw_optimisations(surface):
    title = SMALL_FONT.render("IMPLEMENTED OPTIMISATIONS", True, TEXT_COLOR)
    surface.blit(title, (40, 280))

    lines = [
        "MINIMISE GLOBAL HOLES",
        "MINIMISE HEIGHT",
        "CHECK HELD PIECE",
    ]
    y = 310
    for s in lines:
        text = SMALL_FONT.render(f"--- {s}", True, TEXT_COLOR)
        surface.blit(text, (40, y))
        y += 24


# ============ FULL GAME LOOP WITH AI ============

def reset_game():
    board = create_board()
    held = None
    next_piece = random.choice(PIECES)
    score = 0
    lines_total = 0
    return board, held, next_piece, score, lines_total


def main():
    clock = pygame.time.Clock()

    board, held_piece, next_piece, score, lines_total = reset_game()

    current_piece = next_piece
    next_piece = random.choice(PIECES)

    step_interval = 150
    last_step_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        now = pygame.time.get_ticks()
        if now - last_step_time >= step_interval:
            last_step_time = now

            best_move = choose_best_move(board, current_piece)
            use_held = False

            if held_piece is not None:
                alt_move = choose_best_move(board, held_piece)
                if alt_move is not None and (best_move is None or
                                             alt_move["score"] > best_move["score"]):
                    best_move = alt_move
                    current_piece, held_piece = held_piece, current_piece
                    use_held = True

            if best_move is None:
                print(f"Game over. Total lines: {lines_total}, score: {score}")
                board, held_piece, next_piece, score, lines_total = reset_game()
                current_piece = next_piece
                next_piece = random.choice(PIECES)
            else:
                board = best_move["board"]
                lines_cleared = best_move["lines"]
                lines_total += lines_cleared

                if lines_cleared == 1:
                    score += 40
                elif lines_cleared == 2:
                    score += 100
                elif lines_cleared == 3:
                    score += 300
                elif lines_cleared >= 4:
                    score += 800

                if not use_held and random.random() < 0.05:
                    if held_piece is None:
                        held_piece = current_piece
                        current_piece = next_piece
                        next_piece = random.choice(PIECES)
                    else:
                        held_piece, current_piece = current_piece, held_piece
                else:
                    current_piece = next_piece
                    next_piece = random.choice(PIECES)

        screen.fill(BG_COLOR)

        draw_board(screen, board)
        draw_piece_box(screen, "HELD", HOLD_BOX_X, HOLD_BOX_Y,
                       HOLD_BOX_W, HOLD_BOX_H, held_piece)
        draw_piece_box(screen, "NEXT", NEXT_BOX_X, NEXT_BOX_Y,
                       NEXT_BOX_W, NEXT_BOX_H, next_piece)
        draw_score(screen, score)
        draw_optimisations(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
