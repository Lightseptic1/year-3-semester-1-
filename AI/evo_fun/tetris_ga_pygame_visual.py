import sys
import time
from typing import List, Dict, Tuple
import math
import pygame

from tetris_ga_core import (
    WIDTH,
    HEIGHT,
    simulate_game,
    random_weights,
    evolve_one_generation,
)


# ==== visual config ====
CELL_SIZE = 20
CELL_MARGIN = 1
BG_COLOR = (15, 15, 25)
EMPTY_COLOR = (20, 20, 40)
BLOCK_COLOR = (60, 200, 255)
GRID_COLOR = (40, 40, 60)
TEXT_COLOR = (230, 230, 230)
PIECE_COLORS = {
    0: (20, 20, 40),    # empty
    1: (0, 255, 255),   # I - Cyan
    2: (255, 255, 0),   # O - Yellow
    3: (160, 0, 240),   # T - Purple
    4: (0, 255, 0),     # S - Green
    5: (255, 0, 0),     # Z - Red
    6: (0, 0, 255),     # J - Blue
    7: (255, 165, 0),   # L - Orange
}

CHILDREN_TO_SHOW = None   # None means: show all population

GRID_ROWS = 0  # will be set later
GRID_COLS = 0


SIDE_PANEL_WIDTH = 320
FPS = 20                  # visual speed


def make_window_size() -> Tuple[int, int]:
    board_w = WIDTH * CELL_SIZE + 2 * CELL_MARGIN
    board_h = HEIGHT * CELL_SIZE + 2 * CELL_MARGIN
    win_w = GRID_COLS * board_w + SIDE_PANEL_WIDTH
    win_h = GRID_ROWS * board_h
    return win_w, win_h


def draw_board(
    surface: pygame.Surface,
    board,
    top_left: Tuple[int, int],
):
    x0, y0 = top_left
    # board border
    board_w = WIDTH * CELL_SIZE
    board_h = HEIGHT * CELL_SIZE
    pygame.draw.rect(
        surface,
        GRID_COLOR,
        pygame.Rect(x0 - 2, y0 - 2, board_w + 4, board_h + 4),
        width=2,
    )

    for y in range(HEIGHT):
        for x in range(WIDTH):
            cell = board[y][x]
            cx = x0 + x * CELL_SIZE
            cy = y0 + y * CELL_SIZE
            rect = pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)
            color = PIECE_COLORS.get(cell, (255, 255, 255))
            pygame.draw.rect(surface, color, rect)
            # grid line
            pygame.draw.rect(surface, GRID_COLOR, rect, width=1)


def run_visual_evolution():
    pygame.init()
    pygame.display.set_caption("Genetic Tetris visual")

    win_w, win_h = make_window_size()
    screen = pygame.display.set_mode((win_w, win_h))

    font_small = pygame.font.SysFont("consolas", 16)
    font_big = pygame.font.SysFont("consolas", 20, bold=True)

    clock = pygame.time.Clock()

    # GA settings
    population_size = 45
    generations = 50
    elite_size = 4
    mutation_rate = 0.25
    games_per_individual = 3
    max_pieces_visual = 80

    # create initial population
    population: List[Dict[str, float]] = [random_weights() for _ in range(population_size)]

    for gen in range(generations):
        # evolve one generation
        population, stats = evolve_one_generation(
            population,
            elite_size=elite_size,
            mutation_rate=mutation_rate,
            games_per_individual=games_per_individual,
        )

        sorted_pop = stats["sorted_population"]
        sorted_fit = stats["sorted_fitnesses"]
        best_fit = stats["best_fitness"]
        best_weights = stats["best_weights"]

        print(f"Generation {gen}: best fitness {best_fit:.2f}, best weights {best_weights}")

        # pick top N children to visualise
        num_show = min(CHILDREN_TO_SHOW, len(sorted_pop))
        children = sorted_pop[:num_show]
        children_fitness = sorted_fit[:num_show]

        # for each child, record one game
        runs: List[Tuple[int, List]] = []
        max_steps = 0
        for w in children:
            total_lines, steps = simulate_game(
                w,
                max_pieces=max_pieces_visual,
                record_steps=True,
            )
            runs.append((total_lines, steps))
            if len(steps) > max_steps:
                max_steps = len(steps)

        # play through the recorded steps
        for step_idx in range(max_steps):
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BG_COLOR)

            # draw boards in a grid
            board_w = WIDTH * CELL_SIZE + 2 * CELL_MARGIN
            board_h = HEIGHT * CELL_SIZE + 2 * CELL_MARGIN

            for idx, (total_lines, steps) in enumerate(runs):
                row = idx // GRID_COLS
                col = idx % GRID_COLS
                x_offset = col * board_w + CELL_MARGIN
                y_offset = row * board_h + CELL_MARGIN

                if steps:
                    frame_idx = min(step_idx, len(steps) - 1)
                    board = steps[frame_idx]
                    draw_board(screen, board, (x_offset, y_offset))

                # label for this child
                label = font_small.render(
                    f"Child {idx}  fit {children_fitness[idx]:.1f}  lines {total_lines}",
                    True,
                    TEXT_COLOR,
                )
                screen.blit(label, (x_offset, y_offset - 20))

            # side panel info
            panel_x = GRID_COLS * board_w + 10
            y = 10

            title = font_big.render(f"Generation {gen}", True, TEXT_COLOR)
            screen.blit(title, (panel_x, y))
            y += 30

            best_label = font_small.render(f"Best fitness: {best_fit:.2f}", True, TEXT_COLOR)
            screen.blit(best_label, (panel_x, y))
            y += 25

            screen.blit(font_small.render("Best weights:", True, TEXT_COLOR), (panel_x, y))
            y += 20
            for k, v in best_weights.items():
                txt = font_small.render(f"{k}: {v:+.3f}", True, TEXT_COLOR)
                screen.blit(txt, (panel_x, y))
                y += 18

            y += 10
            screen.blit(font_small.render("Controls:", True, TEXT_COLOR), (panel_x, y))
            y += 20
            screen.blit(font_small.render("Close window to stop", True, TEXT_COLOR), (panel_x, y))

            pygame.display.flip()
            clock.tick(FPS)

    # after evolution, keep best run visible once more
    time.sleep(1.0)
    pygame.quit()


if __name__ == "__main__":
    run_visual_evolution()
