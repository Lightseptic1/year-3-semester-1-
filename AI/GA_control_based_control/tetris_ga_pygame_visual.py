import sys
import time
import math
import csv
from typing import List, Dict, Tuple

import pygame

from tetris_ga_core import (
    WIDTH,
    HEIGHT,
    simulate_game,
    random_weights,
    evolve_one_generation,
)

CELL_SIZE = 8
CELL_MARGIN = 1
BG_COLOR = (15, 15, 25)
EMPTY_COLOR = (20, 20, 40)
GRID_COLOR = (40, 40, 60)
TEXT_COLOR = (230, 230, 230)

# piece colors by ID (0 = empty, 1..7 = tetromino types)
PIECE_COLORS = {
    0: (20, 20, 40),    # empty
    1: (0, 255, 255),   # I
    2: (255, 255, 0),   # O
    3: (160, 0, 240),   # T
    4: (0, 255, 0),     # S
    5: (255, 0, 0),     # Z
    6: (0, 0, 255),     # J
    7: (255, 165, 0),   # L
}

LOSS_BORDER_COLOR = (255, 60, 60)

CHILDREN_TO_SHOW = 50

SIDE_PANEL_WIDTH = 320
FPS = 480  # visual speed

MENU_WIDTH = 640
MENU_HEIGHT = 360


def draw_board(
    surface: pygame.Surface,
    board,
    top_left: Tuple[int, int],
):
    x0, y0 = top_left

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
            pygame.draw.rect(surface, GRID_COLOR, rect, width=1)


# ---------- GENOME VISUAL HELPERS (used in mode 2, but can be reused later) ----------

def draw_fitness_history(
    surface: pygame.Surface,
    history: List[float],
    top_left: Tuple[int, int],
    size: Tuple[int, int],
):
    x0, y0 = top_left
    w, h = size

    rect = pygame.Rect(x0, y0, w, h)
    pygame.draw.rect(surface, (10, 10, 20), rect)
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

    if not history:
        return

    font = pygame.font.SysFont("consolas", 12)
    label = font.render("Best fitness history", True, TEXT_COLOR)
    surface.blit(label, (x0 + 6, y0 + 4))

    pad_top = 22
    pad_bottom = 6
    pad_left = 6
    pad_right = 6

    if len(history) == 1:
        pygame.draw.circle(
            surface,
            (120, 240, 120),
            (x0 + w // 2, y0 + (pad_top + h - pad_bottom) // 2),
            2,
        )
        return

    values = history
    n = len(values)
    v_min = min(values)
    v_max = max(values)
    if math.isclose(v_min, v_max):
        v_min -= 1.0
        v_max += 1.0

    plot_w = w - pad_left - pad_right
    plot_h = h - pad_top - pad_bottom

    def point_for(idx: int) -> Tuple[int, int]:
        t = idx / (n - 1)
        x = x0 + pad_left + int(t * plot_w)
        norm = (values[idx] - v_min) / (v_max - v_min)
        y = y0 + pad_top + int((1.0 - norm) * plot_h)
        return x, y

    pts = [point_for(i) for i in range(n)]

    for i in range(1, len(pts)):
        pygame.draw.line(surface, (120, 240, 120), pts[i - 1], pts[i], 2)

    for p in pts:
        pygame.draw.circle(surface, (200, 255, 200), p, 2)

    last_val = values[-1]
    val_text = font.render(f"{last_val:.1f}", True, TEXT_COLOR)
    surface.blit(val_text, (x0 + w - 60, y0 + 4))


def draw_weight_heatmap(
    surface: pygame.Surface,
    history: List[List[float]],
    top_left: Tuple[int, int],
    size: Tuple[int, int],
    max_weights: int = 16,
):
    if not history:
        return

    x0, y0 = top_left
    w, h = size
    rect = pygame.Rect(x0, y0, w, h)
    pygame.draw.rect(surface, (10, 10, 20), rect)
    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

    font = pygame.font.SysFont("consolas", 12)
    label = font.render("Genome evolution", True, TEXT_COLOR)
    surface.blit(label, (x0 + 6, y0 + 4))

    pad_top = 22
    pad_left = 6
    pad_bottom = 6
    pad_right = 6

    gen_count = len(history)
    weight_count = min(len(history[0]), max_weights)

    if gen_count <= 0 or weight_count <= 0:
        return

    max_abs = 0.0
    for genome in history:
        for i in range(weight_count):
            v = abs(float(genome[i]))
            if v > max_abs:
                max_abs = v
    if max_abs == 0.0:
        max_abs = 1.0

    grid_w = w - pad_left - pad_right
    grid_h = h - pad_top - pad_bottom

    cell_w = max(1, grid_w // gen_count)
    cell_h = max(1, grid_h // weight_count)

    for g_idx, genome in enumerate(history):
        for w_idx in range(weight_count):
            v = float(genome[w_idx])
            mag = min(abs(v) / max_abs, 1.0)

            if v >= 0:
                col = (
                    int(40 + 180 * mag),
                    int(120 + 120 * mag),
                    int(40 + 40 * mag),
                )
            else:
                col = (
                    int(140 + 115 * mag),
                    int(40 + 40 * (1.0 - mag)),
                    int(40 + 40 * (1.0 - mag)),
                )

            cx = x0 + pad_left + g_idx * cell_w
            cy = y0 + pad_top + w_idx * cell_h
            cell_rect = pygame.Rect(cx, cy, cell_w, cell_h)
            pygame.draw.rect(surface, col, cell_rect)

    gen_text = font.render("older  →  newer", True, TEXT_COLOR)
    surface.blit(gen_text, (x0 + pad_left, y0 + h - 18))

    # label first few weights on the right
    for w_idx in range(min(weight_count, 4)):
        name = f"w{w_idx}"
        lbl = font.render(name, True, TEXT_COLOR)
        cy = y0 + pad_top + w_idx * cell_h + 2
        surface.blit(lbl, (x0 + w - pad_right - 40, cy))


# ---------- MODE 1: FULL TETRIS VISUAL (unchanged behavior) ----------

def run_visual_evolution():
    pygame.display.set_caption("Genetic Tetris visual")
    global_best_weights = None
    global_best_fitness = float("-inf")

    font_small = pygame.font.SysFont("consolas", 12)
    font_big = pygame.font.SysFont("consolas", 18, bold=True)

    clock = pygame.time.Clock()

    # GA settings
    population_size = 100
    generations = 5
    elite_size = 6
    mutation_rate = 0.25
    games_per_individual = 1
    max_pieces_visual = 400

    population: List[List[float]] = [random_weights() for _ in range(population_size)]

    screen = None
    prev_best_fit = None

    for gen in range(generations):
        population, stats = evolve_one_generation(
            population,
            elite_size=elite_size,
            mutation_rate=mutation_rate,
            games_per_individual=games_per_individual,
            global_best_weights=global_best_weights,
        )
        sorted_pop = stats["sorted_population"]
        sorted_fit = stats["sorted_fitnesses"]
        best_weights = stats["best_weights"]
        best_fit = stats["best_fitness"]

        if best_fit > global_best_fitness:
            global_best_fitness = best_fit
            global_best_weights = best_weights.copy()
        if prev_best_fit is not None and best_fit < prev_best_fit:
            print(
                f"Skipping generation {gen} (worse fitness: "
                f"{best_fit:.2f} < {prev_best_fit:.2f})"
            )
            prev_best_fit = best_fit
            continue

        print(f"Generation {gen}: best fitness {best_fit:.2f}")

        if CHILDREN_TO_SHOW is None:
            num_show = len(sorted_pop)
        else:
            num_show = min(CHILDREN_TO_SHOW, len(sorted_pop))

        children = sorted_pop[:num_show]
        children_fitness = sorted_fit[:num_show]

        max_cols = 10
        cols = min(num_show, max_cols)
        rows = max(1, math.ceil(num_show / cols))

        board_w = WIDTH * CELL_SIZE + 2 * CELL_MARGIN
        board_h = HEIGHT * CELL_SIZE + 2 * CELL_MARGIN

        win_w = cols * board_w + SIDE_PANEL_WIDTH
        win_h = rows * board_h
        if screen is None or screen.get_width() != win_w or screen.get_height() != win_h:
            screen = pygame.display.set_mode((win_w, win_h))

        runs: List[Tuple[int, List, bool]] = []
        max_steps = 0
        for genome in children:
            total_score, steps, topped_out = simulate_game(
                genome,
                max_pieces=max_pieces_visual,
                record_steps=True,
            )
            runs.append((total_score, steps, topped_out))
            if len(steps) > max_steps:
                max_steps = len(steps)

        for step_idx in range(max_steps):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BG_COLOR)
            live_lines_per_child: List[int] = []

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

                if topped_out:
                    outer_rect = pygame.Rect(
                        x_offset - 4,
                        y_offset - 4,
                        WIDTH * CELL_SIZE + 8,
                        HEIGHT * CELL_SIZE + 8,
                    )
                    pygame.draw.rect(screen, LOSS_BORDER_COLOR, outer_rect, width=4)

                score_text = f"score {children_fitness[idx]:.1f}  lines {live_lines}"
                label = pygame.font.SysFont("consolas", 12).render(
                    score_text, True, TEXT_COLOR
                )
                label_rect = label.get_rect()
                label_rect.centerx = x_offset + (WIDTH * CELL_SIZE) // 2
                label_rect.top = y_offset + 2
                screen.blit(label, label_rect)

            panel_x = cols * board_w + 10
            y = 10

            title = font_big.render(f"Generation {gen}", True, TEXT_COLOR)
            screen.blit(title, (panel_x, y))
            y += 30

            best_label = font_small.render(
                f"Best fitness (current): {best_fit:.2f}", True, TEXT_COLOR
            )
            screen.blit(best_label, (panel_x, y))
            y += 20

            if prev_best_fit is not None:
                prev_label = font_small.render(
                    f"Best fitness (previous): {prev_best_fit:.2f}",
                    True,
                    TEXT_COLOR,
                )
            else:
                prev_label = font_small.render(
                    "Best fitness (previous): N/A", True, TEXT_COLOR
                )
            screen.blit(prev_label, (panel_x, y))
            y += 20

            y += 5
            screen.blit(
                font_small.render("Best genome params:", True, TEXT_COLOR),
                (panel_x, y),
            )
            y += 18

            for i, v in enumerate(best_weights[:10]):
                txt = font_small.render(f"w[{i}]: {v:+.3f}", True, TEXT_COLOR)
                screen.blit(txt, (panel_x, y))
                y += 16

            y += 8
            screen.blit(
                font_small.render("Children scores:", True, TEXT_COLOR),
                (panel_x, y),
            )
            y += 16

            for idx, fit in enumerate(children_fitness):
                live_lines = (
                    live_lines_per_child[idx]
                    if idx < len(live_lines_per_child)
                    else 0
                )
                txt = font_small.render(
                    f"{idx:02d}: {fit:.2f} lines {live_lines}", True, TEXT_COLOR
                )
                screen.blit(txt, (panel_x, y))
                y += 14
                if y > win_h - 40:
                    break

            y += 8
            screen.blit(
                font_small.render("Controls:", True, TEXT_COLOR),
                (panel_x, y),
            )
            y += 16
            screen.blit(
                font_small.render("Close window to stop", True, TEXT_COLOR),
                (panel_x, y),
            )

            pygame.display.flip()
            clock.tick(0)

        prev_best_fit = best_fit

    time.sleep(0.25)
    pygame.quit()


# ---------- MODE 2: GENOME MAP + CSV, NO TETRIS BOARDS ----------

def run_genome_csv_mode(output_path: str = "tetris_ga_results.csv"):
    """
    Mode 2:
    - No Tetris board visualisation
    - Just a small window with fitness history + genome heatmap
    - CSV file with per-generation stats and best genome
    """
    pygame.display.set_caption("Genetic Tetris - Genome evolution")
    # small, side-panel style window
    win_w = SIDE_PANEL_WIDTH
    win_h = 320
    screen = pygame.display.set_mode((win_w, win_h))

    font_small = pygame.font.SysFont("consolas", 12)
    font_big = pygame.font.SysFont("consolas", 18, bold=True)

    clock = pygame.time.Clock()

    # GA settings (same as visual)
    population_size = 100
    generations = 5
    elite_size = 6
    mutation_rate = 0.25
    games_per_individual = 1

    population: List[List[float]] = [random_weights() for _ in range(population_size)]

    global_best_weights = None
    global_best_fitness = float("-inf")

    best_fitness_history: List[float] = []
    best_weights_history: List[List[float]] = []
    max_history = 120

    # CSV setup
    genome_len = len(population[0])
    weight_headers = [f"w{i}" for i in range(genome_len)]
    csv_file = open(output_path, mode="w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    header = [
        "generation",
        "best_fitness",
        "avg_fitness",
        "worst_fitness",
        "global_best_fitness",
    ] + weight_headers
    csv_writer.writerow(header)

    print(f"Running genome mode, logging to {output_path}")

    try:
        for gen in range(generations):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit

            population, stats = evolve_one_generation(
                population,
                elite_size=elite_size,
                mutation_rate=mutation_rate,
                games_per_individual=games_per_individual,
                global_best_weights=global_best_weights,
            )

            sorted_fit = stats["sorted_fitnesses"]
            best_weights = stats["best_weights"]
            best_fit = stats["best_fitness"]
            avg_fit = sum(sorted_fit) / len(sorted_fit)
            worst_fit = sorted_fit[-1]

            if best_fit > global_best_fitness or global_best_weights is None:
                global_best_fitness = best_fit
                global_best_weights = best_weights.copy()

            best_fitness_history.append(best_fit)
            best_weights_history.append(best_weights.copy())
            if len(best_fitness_history) > max_history:
                best_fitness_history.pop(0)
                best_weights_history.pop(0)

            row = [
                gen,
                best_fit,
                avg_fit,
                worst_fit,
                global_best_fitness,
            ] + list(best_weights)
            csv_writer.writerow(row)

            print(
                f"[Genome] Gen {gen}: best={best_fit:.2f} "
                f"avg={avg_fit:.2f} worst={worst_fit:.2f} "
                f"global_best={global_best_fitness:.2f}"
            )

            # draw genome-only window
            screen.fill(BG_COLOR)

            y = 8
            title = font_big.render(f"Generation {gen}", True, TEXT_COLOR)
            screen.blit(title, (8, y))
            y += 26

            best_label = font_small.render(
                f"Best fitness: {best_fit:.2f}", True, TEXT_COLOR
            )
            screen.blit(best_label, (8, y))
            y += 18

            global_label = font_small.render(
                f"Global best: {global_best_fitness:.2f}", True, TEXT_COLOR
            )
            screen.blit(global_label, (8, y))
            y += 6

            # fitness history chart
            fitness_height = 90
            draw_fitness_history(
                screen,
                best_fitness_history,
                (8, y),
                (win_w - 16, fitness_height),
            )
            y += fitness_height + 6

            # weight heatmap
            heatmap_height = win_h - y - 8
            if heatmap_height > 40:
                draw_weight_heatmap(
                    screen,
                    best_weights_history,
                    (8, y),
                    (win_w - 16, heatmap_height),
                    max_weights=16,
                )

            pygame.display.flip()
            clock.tick(0)  # no need to be crazy fast on redraw

    except SystemExit:
        print("Genome mode interrupted by user.")
    finally:
        csv_file.close()
        time.sleep(0.25)
        pygame.quit()
        print("Genome mode finished.")


# ---------- MENU + MAIN ----------

def menu_select_mode() -> str:
    """
    Simple pygame menu that lets the user pick:
    1 = full Tetris visual simulation
    2 = genome map + CSV (no Tetris boards)
    """
    pygame.init()
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Genetic Tetris - Mode select")

    font_title = pygame.font.SysFont("consolas", 28, bold=True)
    font_opt = pygame.font.SysFont("consolas", 20)

    clock = pygame.time.Clock()

    mode = None
    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "visual"
                elif event.key == pygame.K_2:
                    mode = "genome"

        screen.fill(BG_COLOR)

        title = font_title.render("Genetic Tetris", True, TEXT_COLOR)
        screen.blit(
            title,
            title.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 3)),
        )

        opt1 = font_opt.render("1: Visual Tetris simulation", True, TEXT_COLOR)
        opt2 = font_opt.render(
            "2: Genome map + CSV (faster, no boards)", True, TEXT_COLOR
        )

        screen.blit(
            opt1,
            opt1.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 3 + 60)),
        )
        screen.blit(
            opt2,
            opt2.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 3 + 100)),
        )

        pygame.display.flip()
        clock.tick(0)

    return mode


def main():
    mode = menu_select_mode()

    if mode == "visual":
        run_visual_evolution()
    else:
        run_genome_csv_mode("tetris_ga_results.csv")


if __name__ == "__main__":
    main()
