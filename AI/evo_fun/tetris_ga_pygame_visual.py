import sys
import time
import math
from typing import List, Dict, Tuple

import pygame

from tetris_ga_core import (
    WIDTH,
    HEIGHT,
    simulate_game,
    random_weights,
    evolve_one_generation,
)

# ==== visual config ====
CELL_SIZE = 8
CELL_MARGIN = 1
BG_COLOR = (15, 15, 25)
EMPTY_COLOR = (20, 20, 40)
GRID_COLOR = (40, 40, 60)
TEXT_COLOR = (230, 230, 230)

# piece colors by ID (0 = empty, 1..7 = tetromino types)
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

LOSS_BORDER_COLOR = (255, 60, 60)  # red box for topped out boards

# None means: show all individuals in the population
CHILDREN_TO_SHOW = 50

SIDE_PANEL_WIDTH = 320
FPS = 240  # visual speed


def draw_board(
    surface: pygame.Surface,
    board,
    top_left: Tuple[int, int],
):
    x0, y0 = top_left

    board_w = WIDTH * CELL_SIZE
    board_h = HEIGHT * CELL_SIZE

    # border
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
            pygame.draw.rect(surface, GRID_COLOR, rect, width=1)


def run_visual_evolution():
    pygame.init()
    pygame.display.set_caption("Genetic Tetris visual")

    font_small = pygame.font.SysFont("consolas", 12)
    font_big = pygame.font.SysFont("consolas", 18, bold=True)

    clock = pygame.time.Clock()

    # GA settings
    population_size = 30
    generations = 50
    elite_size = 4
    mutation_rate = 0.25
    games_per_individual = 1
    max_pieces_visual = 200

    # initial population
    population: List[Dict[str, float]] = [random_weights() for _ in range(population_size)]

    screen = None  # we will create it once we know rows / cols

    # track previous generation best fitness for display
    prev_best_fit = None

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

        # pick how many children to visualise
        if CHILDREN_TO_SHOW is None:
            num_show = len(sorted_pop)
        else:
            num_show = min(CHILDREN_TO_SHOW, len(sorted_pop))

        children = sorted_pop[:num_show]
        children_fitness = sorted_fit[:num_show]

        # compute grid layout based on num_show
        max_cols = 10
        cols = min(num_show, max_cols)
        rows = max(1, math.ceil(num_show / cols))

        board_w = WIDTH * CELL_SIZE + 2 * CELL_MARGIN
        board_h = HEIGHT * CELL_SIZE + 2 * CELL_MARGIN

        # create / resize window if needed
        win_w = cols * board_w + SIDE_PANEL_WIDTH
        win_h = rows * board_h
        if screen is None or screen.get_width() != win_w or screen.get_height() != win_h:
            screen = pygame.display.set_mode((win_w, win_h))

        # for each child, record one game
        # runs: list of (total_lines, steps, topped_out)
        runs: List[Tuple[int, List, bool]] = []
        max_steps = 0
        for w in children:
            total_score, steps, topped_out = simulate_game(
                w,
                max_pieces=max_pieces_visual,
                record_steps=True,
            )
            runs.append((total_score, steps, topped_out))
            if len(steps) > max_steps:
                max_steps = len(steps)

        # play through recorded steps for this generation
        for step_idx in range(max_steps):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BG_COLOR)
            live_lines_per_child: List[int] = []
            # draw each child board
            for idx, (total_score, steps, topped_out) in enumerate(runs):
                row = idx // cols
                col = idx % cols

                x_offset = col * board_w + CELL_MARGIN
                y_offset = row * board_h + CELL_MARGIN
                live_lines = 0
                if steps:
                    frame_idx = min(step_idx, len(steps) - 1)
                    board, live_lines = steps[frame_idx]
                    draw_board(screen, board, (x_offset, y_offset))
                live_lines_per_child.append(live_lines)
                # big red box overlay if topped out
                if topped_out:
                    outer_rect = pygame.Rect(
                        x_offset - 4,
                        y_offset - 4,
                        WIDTH * CELL_SIZE + 8,
                        HEIGHT * CELL_SIZE + 8,
                    )
                    pygame.draw.rect(screen, LOSS_BORDER_COLOR, outer_rect, width=4)

                # centered label inside top of board to avoid overlap
                score_text = f"score {children_fitness[idx]:.1f}  lines {live_lines}"
                label = font_small.render(score_text, True, TEXT_COLOR)
                label_rect = label.get_rect()
                label_rect.centerx = x_offset + (WIDTH * CELL_SIZE) // 2
                label_rect.top = y_offset + 2
                screen.blit(label, label_rect)

            # side panel info
            panel_x = cols * board_w + 10
            y = 10

            title = font_big.render(f"Generation {gen}", True, TEXT_COLOR)
            screen.blit(title, (panel_x, y))
            y += 30

            # current generation best fitness
            best_label = font_small.render(f"Best fitness (current): {best_fit:.2f}", True, TEXT_COLOR)
            screen.blit(best_label, (panel_x, y))
            y += 20

            # previous generation best fitness
            if prev_best_fit is not None:
                prev_label = font_small.render(
                    f"Best fitness (previous): {prev_best_fit:.2f}",
                    True,
                    TEXT_COLOR,
                )
                screen.blit(prev_label, (panel_x, y))
                y += 20
            else:
                prev_label = font_small.render("Best fitness (previous): N/A", True, TEXT_COLOR)
                screen.blit(prev_label, (panel_x, y))
                y += 20

            y += 5
            screen.blit(font_small.render("Best weights:", True, TEXT_COLOR), (panel_x, y))
            y += 18
            for k, v in best_weights.items():
                txt = font_small.render(f"{k}: {v:+.3f}", True, TEXT_COLOR)
                screen.blit(txt, (panel_x, y))
                y += 16

            y += 8
            # list scores of all children currently on screen
            screen.blit(font_small.render("Children scores:", True, TEXT_COLOR), (panel_x, y))
            y += 16

            for idx, fit in enumerate(children_fitness):
                live_lines = live_lines_per_child[idx] if idx < len(live_lines_per_child) else 0
                txt = font_small.render(f"{idx:02d}: {fit:.2f} lines {live_lines}", True, TEXT_COLOR)
                screen.blit(txt, (panel_x, y))
                y += 14
                # brute guard against drawing offscreen forever
                if y > win_h - 40:
                    break

            y += 8
            screen.blit(font_small.render("Controls:", True, TEXT_COLOR), (panel_x, y))
            y += 16
            screen.blit(font_small.render("Close window to stop", True, TEXT_COLOR), (panel_x, y))

            pygame.display.flip()
            clock.tick(FPS)

        # update previous best fitness at end of generation loop
        prev_best_fit = best_fit

    time.sleep(0.25)
    pygame.quit()


if __name__ == "__main__":
    run_visual_evolution()
